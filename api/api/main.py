import pdfplumber
from fastapi.staticfiles import StaticFiles
from collections import defaultdict
from sklearn.neighbors import NearestNeighbors
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import JSONResponse
from psycopg2.extras import Json
import os
import io
from bs4 import BeautifulSoup
import numpy as np
import shutil
import sys
from api.utils.generators import *
from api.utils.document import Document
from api.utils.line import Line
from api.utils.page import Page
from api.db.db_reader import DBReader
from api.db.db_writer import DBWriter

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
app = FastAPI()
# mount static files
# for docker: /data for both
# for manual: /../container_data/data and ../container_data/data
app.mount("/data", StaticFiles(directory="../../container_data/data"),
          name="data")
origins = [
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db_reader = DBReader()
db_writer = DBWriter()

def get_position(element):
    """Calculate the position of a given BeautifulSoup element.

    Args:
        element (BF element): Element to extract positional attributes from.

    Returns:
        int[]: x position, y position, width and height.
    """
    return float(element['xMin']), float(element['yMin']), float(element['xMax']) - float(element['xMin']), float(element['yMax']) - float(element['yMin'])


@app.get("/")
def root():
    return {"PDFLAT": "API says hi :)"}


def parse_pdf(doc_id, doc_name, doc_path, dataset_id):
    """Extract lines and characters from PDF.

    Args:
        doc_id (int): ID of document.
        doc_path (str): Path to pdf to parse.

    Returns:
        Page[]: List of page objects holding line and char references.
    """

    # Convert pdf to xml using pdftotext
    xml_path = doc_path.replace('.pdf', '.xml')
    os.system(
        f'pdftotext -bbox-layout {doc_path} {xml_path}')
    file_handler = io.open(xml_path,
                           mode="r", encoding="utf-8").read()
    soup = BeautifulSoup(file_handler, 'lxml-xml')
    doc = soup.find('doc')
    doc_pages = doc.select('page')

    pages = []
    chars_by_page = []

    # Extract chars using PDFPlumber
    with pdfplumber.open(doc_path) as pdf:
        for page_nr, page in enumerate(pdf.pages):
            chars_by_page.append(page.chars)
    print("Extracted chars")

    doc_folder = doc_path.replace(".pdf", "/")
    if not os.path.exists(doc_folder):
        os.mkdir(doc_folder)

    if len(chars_by_page) != len(doc_pages):
        return None

    # Creating images of pages
    page_width, page_height = int(np.floor(float(doc_pages[0]['width']))), int(
        np.floor(float(doc_pages[0]['height'])))
    os.system(
        f'pdftocairo -png -scale-to-x {page_width} -scale-to-y {page_height} {doc_path} {doc_folder}page')
    imgs = os.listdir(doc_folder)
    number_of_images = len(imgs)
    number_of_digits = len(str(number_of_images))
    print("Created images")

    # Extract lines using pdftotext
    print("Extracting lines...")
    for page_nr, doc_page in enumerate(doc_pages):
        page_number_starting_at_1 = page_nr + 1
        number_of_zeros = number_of_digits - \
            len(str(page_number_starting_at_1))
        number_of_zeros = max(0, number_of_zeros)
        number_of_zeros = int(number_of_zeros)
        number = '0' * number_of_zeros + str(page_number_starting_at_1)
        image_path = f'/data/{doc_id}/page-{number}.png'

        lines = []
        line_objects = doc_page.select('line')
        for line_nr, line_object in enumerate(line_objects):
            # Create line objects ready for db
            x, y, width, height = get_position(line_object)
            line_text = "PLACEHOLDER"
            line = Line(doc_id, page_nr, line_nr,
                        line_text, x, y, width, height)
            lines.append(line)

        pages.append(Page(doc_id, page_nr, image_path, page_width,
                     page_height, lines, chars_by_page[page_nr]))

    return Document(doc_id, doc_name, dataset_id, pages)


@app.post("/upload_pdf/{dataset_id}")
def upload(file_obj: UploadFile, dataset_id: str):
    print('uploading pdf...')

    # Check if file is PDF
    if file_obj.content_type != 'application/pdf':
        print(f'ivalid file type ({file_obj.content_type})')
        return {'success': False, 'message': 'file is not a pdf', 'doc_id': None}

    # Extract name and generate ID
    doc_name = file_obj.filename.replace('.pdf', '')
    doc_id = md5_from_string(doc_name + dataset_id)

    # Store a copy of the file
    doc_path = f'../../container_data/data/{doc_id}.pdf'
    with open(doc_path, "wb") as buffer:
        shutil.copyfileobj(file_obj.file, buffer)
    print(f'stored file {doc_id}.pdf')

    # Insert the document into the database
    parsed_pdf = parse_pdf(doc_id, doc_name, doc_path, dataset_id)
    print("Parsed file")
    if parsed_pdf is None:
        return {'success': False, 'message': 'document has nothing to annotate', 'doc_id': doc_id}
    elif not db_writer.insert_document(parsed_pdf):
        return {'success': False, 'message': 'document already exists', 'doc_id': doc_id}
    print("Uploaded to database")

    return JSONResponse({'document_id': doc_id})


@ app.post("/dataset")
async def create_dataset(request: Request):
    data = await request.json()
    name = data.get("name")
    dataset_id = md5_from_string(name)
    if not db_writer.insert_dataset(dataset_id, name):
        return {'success': False, 'message': 'dataset already exists', 'dataset': db_reader.get_dataset(dataset_id)}
    return {'success': True, 'message': 'dataset created', 'dataset': db_reader.get_dataset(dataset_id)}


@ app.post("/label_region")
async def label_region(request: Request):
    data = await request.json()
    document_id = data.get("document_id")
    page_nr = data.get("page_nr")
    number = data.get("number")
    type = data.get("type")
    label_id = data.get("label_id")
    if type == "line":
        db_writer.label_line(document_id, page_nr, number, label_id)
    elif type == "char":
        db_writer.label_char(document_id, page_nr, number, label_id)
    return {'success': True, 'message': 'region labeled', 'label_id': label_id}


@ app.delete("/char/")
def delete_char(document_id, page_nr, char_nr):
    if db_writer.delete_char(document_id, page_nr, char_nr):
        return {'success': True, 'message': 'region deleted'}
    return {'success': False, 'message': 'delete failed'}


@ app.delete("/line/")
def delete_line(document_id, page_nr, line_nr):
    if db_writer.delete_line(document_id, page_nr, line_nr):
        return {'success': True, 'message': 'region deleted'}
    return {'success': False, 'message': 'delete failed'}


@ app.post("/merge_lines")
async def merge_lines(request: Request):
    data = await request.json()
    line_nrs = data.get("region_ids")
    document_id = data.get("document_id")
    page_nr = data.get("page_nr")
    regions = [db_reader.get_line(document_id, page_nr, line_nr)
               for line_nr in line_nrs]
    x = min([region['x'] for region in regions])
    y = min([region['y'] for region in regions])
    width = max([region["x"] + region["width"] for region in regions]) - x
    height = max([region["y"] + region["height"] for region in regions]) - y
    text = "\n".join([region['line_text'] for region in regions])
    merged_from = list(set([fr for region in regions for fr in region["merged"] if fr != {}] + [region["line_nr"] for region in regions]))

    success, line_nr = db_writer.insert_merged_line(
        document_id, page_nr, text, x, y, width, height, merged_from)

    if success:
        return {'success': True, 'message': 'regions merged', 'region': db_reader.get_line(document_id, page_nr, line_nr), "delete_line_nrs": line_nrs}
    return {'success': False, 'message': 'regions could not be merged'}


# @ app.get("/get_labels")
# def get_labels(dataset_id):
#     return JSONResponse({'labels': get_labels_for_dataset(dataset_id)})


@ app.get("/datasets")
def get_datasets():
    return JSONResponse({'datasets': db_reader.get_all_datasets()})


@ app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id):
    print({'dataset': db_reader.get_dataset(dataset_id)})
    return JSONResponse({'dataset': db_reader.get_dataset(dataset_id)})


@ app.get("/documents/{document_id}")
def get_document(document_id):
    document = db_reader.get_document(document_id)
    pages = db_reader.get_pages_of_document(document_id)
    return JSONResponse({'document': document, "pages": pages})


@ app.get("/pages/")
def get_page(document_id, page_nr):
    try:
        page = db_reader.get_page(document_id, page_nr)
        lines = db_reader.get_lines_of_page(document_id, page_nr)
        chars = db_reader.get_chars_of_page(document_id, page_nr)
    except Exception as e:
        return JSONResponse({"success": False})
    return JSONResponse({"success": True, 'page': page, "lines": lines, "chars": chars})


@ app.get("/get_documents_of_dataset/{dataset_id}")
def get_documents_of_dataset(dataset_id):
    try:
        res = JSONResponse(
            {"documents": db_reader.get_documents_of_dataset(dataset_id)})
    except Exception:
        return JSONResponse({"documents": []})
    return res


@ app.post("/delete_document")
async def delete_document(request: Request):
    data = await request.json()
    document_id = data.get("document_id")
    if db_writer.delete_document(document_id):
        return {'success': True, 'message': 'Document, pages, lines and chars deleted'}
    return {'success': False, 'message': 'Nothing with this documentID in db'}


@ app.post("/delete_page")
async def delete_page(request: Request):
    data = await request.json()
    document_id = data.get("document_id")
    page_nr = data.get("page_nr")
    db_writer.delete_page(document_id, page_nr)
    return {'success': True, 'message': 'page deleted'}


@ app.post("/create_label_for_dataset")
async def create_label_for_dataset(request: Request):
    data = await request.json()
    dataset_id = data.get("dataset_id")
    name = data.get("name")
    color = db_reader.get_available_color_for_dataset(dataset_id)
    id = db_reader.get_next_label_id_for_dataset(dataset_id)
    db_writer.set_label_for_dataset(dataset_id, {'id': id, 'name': name, 'color': color})
    return {'success': True, 'message': 'label created', 'label': {'id': id, 'name': name, 'color': color}}


@ app.post("/delete_label_for_dataset")
async def delete_label_for_dataset(request: Request):
    data = await request.json()
    dataset_id = data.get("dataset_id")
    label = data.get("label")
    db_writer.remove_label_for_dataset(dataset_id, Json(label), label)
    return {'success': True, 'message': 'label deleted'}


# @ app.post("/download_dataset")
# async def download_dataset(dataset_id):
#     dataset = get_dataset_from_db(dataset_id)

#     # get pages from db
#     pages = get_all_labelled_pages_from_db(dataset_id)

#     # get regions for each page:
#     regions = []
#     for page in pages:
#         regions.extend(get_regions_for_page(
#             page['document_id'], page['page_nr']))

#     # get labels for dataset
#     labels = get_labels_for_dataset(dataset_id)

#     # label nodes based on region label

#     for page in pages:
#         # select regions with document_id and page_nr
#         regions_on_page = [region for region in regions if region['document_id']
#                            == page['document_id'] and region['page_nr'] == page['page_nr']]
#         for node in page['nodes']:
#             # check if node is within the region using x_center for each node
#             for region in regions_on_page:
#                 if node['x_center'] > region['x_min'] and node['x_center'] < region['x_max'] and node['y_center'] > region['y_min'] and node['y_center'] < region['y_max']:
#                     node['label'] = region['label']
#                     node['region_id'] = region['region_id']
#                     break

#     # remove nodes without label or label below zero
#     for page in pages:
#         page['nodes'] = [node for node in page['nodes']
#                          if node.get('label') != None and node['label'] >= 0]

#     return {
#         'dataset': dataset,
#         'pages': pages,
#         'regions': regions,
#         'labels': labels
#     }
