from .base import connect, close
import pandas as pd
import numpy as np

# retrieve by id function
def get_row_by_id(table, id):
    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data
    sql = f"""SELECT * FROM {table} WHERE {table[:-1]}_id = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (id,))

    row = cur.fetchone()

    close(conn, cur)

    if row:
        return row
    raise Exception(f'No row with id {id} in table {table}')

def get_all_rows(table):
    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data
    sql = f"""SELECT * FROM {table};"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql)

    rows = list(cur.fetchall())
    close(conn, cur)

    return rows

def get_datasets_from_db():
    return get_all_rows('datasets')

def get_dataset_from_db(dataset_id):
    return get_row_by_id('datasets', dataset_id)

def get_page_from_db(document_id, page_nr):
    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data
    sql = """SELECT * FROM pages WHERE document_id = %s AND page_nr = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (document_id, page_nr))

    page = cur.fetchone()

    close(conn, cur)

    if page:
        return page
    raise Exception(f'No page with id {page_nr} in table pages')


def get_labels_for_dataset(dataset_id):
    dataset = get_dataset_from_db(dataset_id)
    return dataset['labels']

def get_document_from_db(document_id):
    conn, cur = connect(dicts=True)
    sql = "SELECT * FROM documents WHERE document_id = %s"
    values = (document_id,)
    cur.execute(sql, values)
    res = cur.fetchall()
    close(conn, cur)
    if res:
        return res
    raise Exception(f'No document with document_id {document_id} in table pages')

def get_pages_of_document(document_id):
    conn, cur = connect(dicts=True)
    sql = "SELECT * FROM pages WHERE document_id = %s"
    values = (document_id,)
    cur.execute(sql, values)
    res = cur.fetchall()
    close(conn, cur)
    if res:
        return res
    raise Exception(f'No page with document_id {document_id} in table pages')

def get_lines_of_page(document_id, page_nr):
    conn, cur = connect(dicts=True)
    sql = "SELECT * FROM lines WHERE document_id = %s and page_nr = %s"
    values = (document_id, page_nr)
    cur.execute(sql, values)
    res = cur.fetchall()
    close(conn, cur)
    if res:
        return res
    raise Exception(f'No line with (document_id, page_nr) {document_id}, {page_nr} in table lines')

def get_line_from_db(document_id, page_nr, line_nr):
    conn, cur = connect(dicts=True)
    sql = "SELECT * FROM lines WHERE document_id = %s and page_nr = %s and line_nr = %s"
    values = (document_id, page_nr, line_nr)
    cur.execute(sql, values)
    res = cur.fetchone()
    close(conn, cur)
    if res:
        return res
    raise Exception(f'No line with (document_id, page_nr, line_nr) {document_id}, {page_nr}, {line_nr} in table lines')

def get_chars_of_page(document_id, page_nr):
    conn, cur = connect(dicts=True)
    sql = "SELECT * FROM chars WHERE document_id = %s and page_nr = %s"
    values = (document_id, page_nr)
    cur.execute(sql, values)
    res = cur.fetchall()
    close(conn, cur)
    if res:
        return res
    raise Exception(f'No char with (document_id, page_nr) {document_id}, {page_nr} in table chars')

def db_get_documents_of_dataset(dataset_id):
    conn, cur = connect()
    sql = "SELECT * FROM documents WHERE dataset_id = %s"
    cur.execute(sql, (dataset_id,))
    res = list(cur.fetchall())
    print(res)
    close(conn, cur)
    if res:
        return res
    raise Exception(f'No docuemnt with dataset_id {dataset_id} in table documents')


def get_available_color_for_dataset(dataset_id):
    # tailwind colors
    COLORS = ['gray', 'red', 'orange', 'yellow', 'green', 'teal', 'blue', 'indigo', 'purple', 'pink', 'amber', 'lime', 'emerald', 'cyan', 'sky', 'violet', 'fuchsia', 'rose']
    # get all labels for this dataset
    labels = get_labels_for_dataset(dataset_id)
    # get all colors that are already used
    used_colors = [label['color'] for label in labels]
    # get all colors that are not used
    available_colors = [color for color in COLORS if color not in used_colors]
    # return a random elment from the available colors
    return np.random.choice(available_colors)
    

def get_next_label_id_for_dataset(dataset_id):
    # get all labels for this dataset
    labels = get_labels_for_dataset(dataset_id)
    # get all label ids
    label_ids = [label['id'] for label in labels]
    # get the next label id
    next_label_id = max(label_ids) + 1
    return next_label_id

def get_highest_line_nr(document_id, page_nr):
     # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data

    sql = """SELECT MAX(line_nr) from lines WHERE document_id = %s AND page_nr = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (document_id, page_nr))

    highest_number = dict(cur.fetchone())

    close(conn, cur)

    return highest_number["max"]