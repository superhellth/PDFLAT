from utils.db import *
from utils.generators import *
from utils.page import Page
from utils.line import Line
from utils.document import Document
import pdfplumber
import pandas as pd
from fastapi.staticfiles import StaticFiles
from collections import defaultdict
from sklearn.neighbors import NearestNeighbors
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import JSONResponse
# from psycopg2.extras import Json
import os
import json
import io
from bs4 import BeautifulSoup
import numpy as np
import shutil
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()

# mount static files
# for docker: /data for both
# for manual: /../container_data/data and ../container_data/data
app.mount("/../container_data/data", StaticFiles(directory="../container_data/data"),
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

    doc_folder = doc_path.replace(".pdf", "/")
    if not os.path.exists(doc_folder):
        os.mkdir(doc_folder)

    if len(chars_by_page) != len(doc_pages):
        return None

    # Extract lines using pdftotext
    for page_nr, doc_page in enumerate(doc_pages):
        page_width, page_height = int(np.floor(float(doc_page['width']))), int(
            np.floor(float(doc_page['height'])))
        os.system(
            f'pdftocairo -png -scale-to-x {page_width} -scale-to-y {page_height} {doc_path} {doc_folder}page')
        imgs = os.listdir(doc_folder)

        number_of_images = len(imgs)
        page_number_starting_at_1 = page_nr + 1
        number_of_digits = len(str(number_of_images))
        number_of_zeros = number_of_digits - \
            len(str(page_number_starting_at_1))
        number_of_zeros = max(0, number_of_zeros)
        number_of_zeros = int(number_of_zeros)
        number = '0' * number_of_zeros + str(page_number_starting_at_1)

        image_path = f'{doc_folder}page-{number}.png'

        lines = []
        line_objects = doc_page.select('line')
        for line_nr, line_object in enumerate(line_objects):
            # Create line objects ready for db
            x, y, width, height = get_position(line_object)
            line_text = "PLACEHOLDER"
            line = Line(doc_id, page_nr, line_nr, line_text, x, y, width, height)
            lines.append(line)

        pages.append(Page(doc_id, page_nr, image_path, page_width, page_height, lines, chars_by_page[page_nr]))

    return Document(doc_id, doc_name, dataset_id, pages)

# print(parse_pdf(0, "test-pdf", "./container_data/data/6dc82e492ffa883f8f42163895d246f9.pdf", 0))


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
    doc_path = f'../container_data/data/{doc_id}.pdf'
    with open(doc_path, "wb") as buffer:
        shutil.copyfileobj(file_obj.file, buffer)
    print(f'stored file {doc_id}.pdf')

    # Insert the document into the database
    parsed_pdf = parse_pdf(doc_id, doc_name, doc_path, dataset_id)
    if parsed_pdf is None:
        return {'success': False, 'message': 'document has nothing to annotate', 'doc_id': doc_id}
    elif not insert_document(parsed_pdf):
        return {'success': False, 'message': 'document already exists', 'doc_id': doc_id}

    return JSONResponse({'document_id': doc_id})


@ app.post("/dataset")
async def create_dataset(request: Request):
    data = await request.json()
    name = data.get("name")
    dataset_id = md5_from_string(name)
    if not insert_dataset(dataset_id, name):
        return {'success': False, 'message': 'dataset already exists', 'dataset': get_dataset_from_db(dataset_id)}
    return {'success': True, 'message': 'dataset created', 'dataset': get_dataset_from_db(dataset_id)}


# @ app.post("/region")
# async def create_region(request: Request):
#     data = await request.json()
#     document_id = data.get("document_id")
#     page_nr = data.get("page_nr")
#     x_min = data.get("x_min")
#     x_max = data.get("x_max")
#     y_min = data.get("y_min")
#     y_max = data.get("y_max")
#     success, region_id, delete_region_ids = create_and_insert_region(
#         document_id, page_nr, x_min, y_min, x_max, y_max)
#     if success:
#         return {'success': True, 'message': 'region created', 'region': get_region_from_db(region_id), 'delete_region_ids': delete_region_ids}
#     if region_id is not None:
#         return {'success': False, 'message': 'region already exists', 'region': get_region_from_db(region_id)}
#     return {'success': False, 'message': 'empty region', 'region': None}


# @ app.get("/region/{region_id}")
# def get_region(region_id):
#     region = get_region_from_db(region_id)
#     return JSONResponse({'region': region})


# @ app.post("/label_region")
# async def label_region(request: Request):
#     data = await request.json()
#     region_id = data.get("region_id")
#     label_id = data.get("label_id")
#     label_region_in_db(region_id, label_id)
#     return {'success': True, 'message': 'region labeled', 'region_id': region_id, 'label_id': label_id}


# @ app.delete("/region/{region_id}")
# def delete_region(region_id):
#     if delete_region_from_db(region_id):
#         return {'success': True, 'message': 'region deleted', 'region_id': region_id}
#     return {'success': False, 'message': 'delete failed', 'region_id': region_id}


# @ app.post("/merge_regions")
# async def merge_regions(request: Request):
#     data = await request.json()
#     region_ids = data.get("region_ids")
#     regions = [get_region_from_db(region_id) for region_id in region_ids]
#     # TODO: implement this with a single db call
#     document_id = regions[0]['document_id']
#     page_nr = regions[0]['page_nr']
#     x_min = min([region['x_min'] for region in regions])
#     y_min = min([region['y_min'] for region in regions])
#     x_max = max([region['x_max'] for region in regions])
#     y_max = max([region['y_max'] for region in regions])

# #    for region_id in region_ids:
# #        delete_region_from_db(region_id)

#     success, region_id, delete_region_ids = create_and_insert_region(
#         document_id, page_nr, x_min, y_min, x_max, y_max)

#     if success:
#         return {'success': True, 'message': 'regions merged', 'region': get_region_from_db(region_id), 'delete_region_ids': delete_region_ids}
#     return {'success': False, 'message': 'regions could not be merged', 'region': get_region_from_db(region_id)}


# @ app.get("/get_labels")
# def get_labels(dataset_id):
#     return JSONResponse({'labels': get_labels_for_dataset(dataset_id)})


@ app.get("/datasets")
def get_datasets():
    return JSONResponse({'datasets': get_datasets_from_db()})

@ app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id):
    print({'dataset': get_dataset_from_db(dataset_id)})
    return JSONResponse({'dataset': get_dataset_from_db(dataset_id)})

@ app.get("/documents/{document_id}")
def get_document(document_id):
    document = dict(get_document_from_db(document_id)[0])
    pages = get_pages_of_document(document_id)
    pages = [dict(page) for page in pages]
    return JSONResponse({'document': document, "pages": pages}) # TODO: add lines and chars

# @ app.get("/get_unlabelled_page/{dataset_id}")
# def get_unlabelled_page(dataset_id):
#     # return get_pages_of_document()
#     page = get_unlabelled_page_from_db(dataset_id)
#     regions = get_regions_for_page(page['document_id'], page['page_nr'])
#     return JSONResponse({'page': page, 'regions': regions})

@ app.get("/get_documents_of_dataset/{dataset_id}")
def get_documents_of_dataset(dataset_id):
    try:
        res = JSONResponse({"documents": db_get_documents_of_dataset(dataset_id)})
    except Exception:
        return JSONResponse({"documents": []})
    return res

@ app.post("/delete_document")
async def delete_document(request: Request):
    data = await request.json()
    document_id = data.get("document_id")
    if delete_document_from_db(document_id):
        return {'success': True, 'message': 'Document, pages, lines and chars deleted'}
    return {'success': False, 'message': 'Nothing with this documentID in db'}

# @ app.post("/label_page")
# async def label_page(request: Request):
#     data = await request.json()
#     document_id = data.get("document_id")
#     page_nr = data.get("page_nr")
#     label_page_in_db(document_id, page_nr)
#     return {'success': True, 'message': 'page set to labeled'}


# @ app.post("/delete_page")
# async def delete_page(request: Request):
#     data = await request.json()
#     document_id = data.get("document_id")
#     page_nr = data.get("page_nr")
#     delete_page_from_db(document_id, page_nr)
#     return {'success': True, 'message': 'page deleted'}


# @ app.post("/create_label_for_dataset")
# async def create_label_for_dataset(request: Request):
#     data = await request.json()
#     dataset_id = data.get("dataset_id")
#     name = data.get("name")
#     color = get_available_color_for_dataset(dataset_id)
#     id = get_next_label_id_for_dataset(dataset_id)
#     set_label_for_dataset(dataset_id, {'id': id, 'name': name, 'color': color})
#     return {'success': True, 'message': 'label created', 'label': {'id': id, 'name': name, 'color': color}}


# @ app.post("/delete_label_for_dataset")
# async def delete_label_for_dataset(request: Request):
#     data = await request.json()
#     dataset_id = data.get("dataset_id")
#     label = data.get("label")
#     remove_label_for_dataset(dataset_id, Json(label))
#     return {'success': True, 'message': 'label deleted'}


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
