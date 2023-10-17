# from utils.db import *
from utils.generators import *
from utils.page import Page
from utils.line import Line
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
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# app = FastAPI()

# # mount static files
# # for docker: /data for both
# app.mount("/../container_data/data", StaticFiles(directory="../container_data/data"),
#           name="data")

# origins = [
#     "*"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


def get_position(element):
    # x, y, w, h
    return float(element['xMin']), float(element['yMin']), float(element['xMax']) - float(element['xMin']), float(element['yMax']) - float(element['yMin'])


# @app.get("/")
def root():
    return {"PDFLAT": "API says hi :)"}


def parse_pdf(doc_id, doc_path, doc_folder):
    xml_path = doc_path.replace('.pdf', '.xml')

    os.system(
        f'pdftotext -bbox-layout {doc_path} {xml_path}')
    file_handler = io.open(xml_path,
                           mode="r", encoding="utf-8").read()
    soup = BeautifulSoup(file_handler, 'lxml-xml')
    doc = soup.find('doc')
    doc_pages = doc.select('page')

    pages = []
    lines = []
    chars = []
    for page_nr, doc_page in enumerate(doc_pages):
        page_width, page_height = int(np.floor(float(doc_page['width']))), int(
            np.floor(float(doc_page['height'])))

        line_objects = doc_page.select('line')
        for line_nr, line_object in enumerate(line_objects):
            # Create line objects ready for db
            x, y, width, height = get_position(line_object)
            line = Line(doc_id, page_nr, line_nr, x, y, width, height)
            lines.append(line)

        pages.append(Page(doc_id, page_nr, page_width, page_height, lines, chars))
        lines = []

    # with pdfplumber.open(document.path) as pdf:

    return pages

print(parse_pdf(0, "./container_data/data/6dc82e492ffa883f8f42163895d246f9.pdf", "./container_data/data/"))

# @app.post("/upload_pdf/{dataset_id}")
# def upload(file_obj: UploadFile, dataset_id: str):
#     print('uploading pdf...')
#     if file_obj.content_type != 'application/pdf':
#         print(f'ivalid file type ({file_obj.content_type})')
#         return {'success': False, 'message': 'file is not a pdf', 'doc_id': None}

#     doc_name = file_obj.filename.replace('.pdf', '')
#     doc_id = md5_from_string(doc_name + dataset_id)

#     if not insert_documents(pd.DataFrame({'document_id': [doc_id], 'title': [doc_name], 'dataset_id': [dataset_id]})):
#         return {'success': False, 'message': 'document already exists', 'doc_id': doc_id}

#     doc_folder = f'/data/{doc_id}/'
#     doc_path = f'/data/{doc_id}.pdf'
#     os.mkdir(doc_folder)

#     with open(doc_path, "wb") as buffer:
#         shutil.copyfileobj(file_obj.file, buffer)

#     print(f'stored file {doc_id}.pdf')
#     pages, nodes, regions = parse_pdf(doc_id, doc_path, doc_folder)

#     nodes_df = pd.DataFrame(dict(nodes))
#     insert_nodes(nodes_df)

#     for page in pages:
#         page_nodes = get_nodes_in_region(
#             doc_id, page['page_nr'], 0, 0, page['page_width'], page['page_height'])

#         # order by node_nr
#         page_nodes = page_nodes.sort_values(by=['node_nr'])
#         # set node number to consecutive numbers starting at 0
#         page_nodes['node_nr'] = range(len(page_nodes))

#         graphs = {}
#         for method in ['1NN', '2NN', '3NN']:
#             graphs[method] = compute_graph_from_nodes(
#                 page_nodes, method=method)

#         page['nodes'] = [Json(x) for x in page_nodes.to_dict('records')],
#         page['graphs'] = json.dumps(graphs)

#     pages_df = pd.DataFrame(pages)

#     insert_pages(pages_df)
#     for region in regions:
#         create_and_insert_region(**region)

#     # return a json response with a list of all images
#     return JSONResponse({'document_id': doc_id})


# @ app.post("/dataset")
# async def create_dataset(request: Request):
#     data = await request.json()
#     name = data.get("name")
#     dataset_id = md5_from_string(name)
#     if not insert_datasets(pd.DataFrame({'dataset_id': [dataset_id], 'name': [name]})):
#         return {'success': False, 'message': 'dataset already exists', 'dataset': get_dataset_from_db(dataset_id)}
#     return {'success': True, 'message': 'dataset created', 'dataset': get_dataset_from_db(dataset_id)}


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


# @ app.get("/datasets")
# def get_datasets():
#     return JSONResponse({'datasets': get_datasets_from_db()})


# @ app.get("/datasets/{dataset_id}")
# def get_dataset(dataset_id):
#     return JSONResponse({'dataset': get_dataset_from_db(dataset_id)})


# @ app.get("/get_unlabelled_page/{dataset_id}")
# def get_unlabelled_page(dataset_id):
#     page = get_unlabelled_page_from_db(dataset_id)
#     regions = get_regions_for_page(page['document_id'], page['page_nr'])
#     return JSONResponse({'page': page, 'regions': regions})


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
