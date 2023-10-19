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

# retrieve by ids function
def get_rows_by_ids(table, ids):
    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data
    sql = f"""SELECT * FROM {table} WHERE id = ANY(%s);"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (ids,))

    rows = list(cur.fetchall())
    close(conn, cur)

    return rows

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

def get_page_from_db(page_id):
    document_id, page_nr = page_id.split('-')

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
    raise Exception(f'No page with id {page_id} in table pages')


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

def get_regions_in_region(document_id, page_nr, x_min, y_min, x_max, y_max):
    # get all regions in the database that are in this region of the page

    x_min = x_min - 2
    x_max = x_max + 2
    y_min = y_min - 2
    y_max = y_max + 2

    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data

    sql = """SELECT * FROM regions WHERE document_id = %s AND page_nr = %s AND x_min >= %s AND x_max <= %s AND y_min >= %s AND y_max <= %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (document_id, page_nr, x_min, x_max, y_min, y_max))

    regions = list(cur.fetchall())

    close(conn, cur)

    return regions


def get_unlabelled_page_from_db(dataset_id):
    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data

    sql = """
    SELECT p.*
    FROM pages p
    JOIN documents d ON p.document_id = d.document_id
    WHERE p.labelled = false
    AND d.dataset_id = %s;
    """

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (dataset_id,))

    page = cur.fetchone()

    close(conn, cur)

    if page:
        return dict(page)
    raise Exception(f'No unlabelled page in dataset {dataset_id}')


def get_all_labelled_pages_from_db(dataset_id):
    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data

    sql = """
    SELECT p.*
    FROM pages p
    JOIN documents d ON p.document_id = d.document_id
    WHERE p.labelled = true
    AND d.dataset_id = %s;
    """

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (dataset_id,))

    pages = list(cur.fetchall())

    close(conn, cur)

    if pages:
        return pages
    raise Exception(f'No labelled pages in dataset {dataset_id}')



def get_regions_for_page(document_id, page_nr):
    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data

    sql = """
        SELECT * from regions WHERE document_id = %s AND page_nr = %s;
        """

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (document_id, page_nr))

    regions = list(cur.fetchall())

    close(conn, cur)

    return regions


def get_region(region_id):
    # Connect to the database
    conn, cur = connect(dicts=True)

    # Define the SQL query to get the data

    sql = """
        SELECT r.graphs, r.document_id, r.page_nr, r.region_id, r.x_min, r.x_max, r.y_min, r.y_max, r.label,
            (
                SELECT json_agg(json_build_object(
                            'node_nr', n.node_nr,
                            'x_min', n.x_min,
                            'x_max', n.x_max,
                            'y_min', n.y_min,
                            'y_max', n.y_max,
                            'features', n.features
                        ))
                FROM nodes n
                WHERE r.document_id = n.document_id AND r.page_nr = n.page_nr
            ) AS nodes
        FROM regions r
        WHERE r.region_id = %s
    """

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (region_id,))

    region = cur.fetchone()

    close(conn, cur)

    return region

def get_labelled_region_ids_for_dataset(dataset_id):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data

    sql = """
        SELECT r.region_id
        FROM regions r join documents d on r.document_id = d.document_id
        WHERE d.dataset_id = %s AND r.label >= 0;
    """

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (dataset_id,))

    region_ids = list(cur.fetchall())

    close(conn, cur)

    return region_ids

def get_labelled_page_ids_for_dataset(dataset_id):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data

    sql = """
        SELECT p.document_id, p.page_nr
        FROM pages p join documents d on p.document_id = d.document_id
        WHERE d.dataset_id = %s AND p.labelled = true;
    """

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (dataset_id,))

    page_ids = list(cur.fetchall())

    close(conn, cur)

    return page_ids

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