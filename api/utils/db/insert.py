from utils.document import Document
from utils.page import Page
from utils.line import Line
from utils.db.getters import get_highest_line_nr
from psycopg2.errors import UniqueViolation
from .base import connect, close

def insert_document(document: Document):
    """Insert a document into the database. Including adding the pages, lines and chars
    into the according tables.

    Args:
        document (Document): The document to index.

    Returns:
        bool: Whether or not the insert was successful.
    """
    # Connect to the database
    conn, cur = connect()

    # Insert document
    sql = "INSERT INTO documents (document_id, title, dataset_id) VALUES (%s, %s, %s);"
    values = (document.document_id, document.title, document.dataset_id)
    try:
        cur.execute(sql, values)
    except UniqueViolation as e:
        return False

    # Insert pages
    for page in document.pages:
        if not insert_page(page, cur):
            return False

    close(conn, cur)
    return True

def insert_dataset(dataset_id, dataset_name):
    """Insert dataset into the database.

    Args:
        dataset_id (int): ID of the dataset to index.
        dataset_name (str): Name of the dataset to index.

    Returns:
        bool: Whether or not the insert was successful.
    """
    # Connect to the database
    conn, cur = connect()

    # Insert dataset
    sql = "INSERT INTO datasets (dataset_id, name) VALUES (%s, %s);"
    values = (dataset_id, dataset_name)
    try:
        cur.execute(sql, values)
    except UniqueViolation as e:
        return False

    close(conn, cur)
    return True

def insert_page(page: Page, cur):
    """Insert page into the database. Including adding the lines and chars.

    Args:
        page (Page): The page to index.
        cur (?): Database connection.

    Returns:
        bool: Whether or not the insert was successful.
    """
    # Insert page
    sql = "INSERT INTO pages (document_id, page_nr, image_path, page_width, page_height, number_lines, number_chars) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    values = (page.document_id, page.page_nr, page.image_path, page.width, page.height, page.number_lines, page.number_chars)
    try:
        cur.execute(sql, values)
    except UniqueViolation as e:
        return False

    # Insert lines
    for line in page.lines:
        if not insert_line(line, cur):
            return False

    # Insert chars
    for char_nr, char in enumerate(page.chars):
        if not insert_char(page.document_id, page.page_nr, char_nr, char, cur):
            return False

    return True

def insert_line(line: Line, cur):
    """Insert line into database.

    Args:
        line (Line): Line to index.
        cur (?): Connection to database.

    Returns:
        bool: Whether or not the insert was successful.
    """
    sql = "INSERT INTO lines (document_id, page_nr, line_nr, line_text, x, y, width, height) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
    values = (line.document_id, line.page_nr, line.line_nr, line.text, line.x, line.y, line.width, line.height)
    try:
        cur.execute(sql, values)
    except UniqueViolation as e:
        return False

    return True

def insert_char(document_id, page_nr, char_nr, char, cur):
    """Insert char into database.

    Args:
        document_id (int): ID of the corresponding document.
        page_nr (int): Number of the corresponding page.
        char_nr (int): Number of this char.
        char (dict): The char object.
        cur (?): Connection to the database.

    Returns:
        bool: Whether or not the insert was successful.
    """
    sql = "INSERT INTO chars (document_id, page_nr, char_nr, char_text, x, y, width, height) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
    values = (document_id, page_nr, char_nr, char["text"], char["x0"], char["y0"], char["width"], char["height"])
    try:
        cur.execute(sql, values)
    except UniqueViolation as e:
        return False

    return True

def create_and_insert_line(document_id, page_nr, text, x, y, width, height):
    conn, cur = connect()
    line_nr = get_highest_line_nr(document_id, page_nr) + 1
    sql = "INSERT INTO lines (document_id, page_nr, line_nr, line_text, x, y, width, height, merged) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
    values = (document_id, page_nr, line_nr, text, x, y, width, height, True)
    try:
        cur.execute(sql, values)
    except UniqueViolation as e:
        return False, None
    
    close(conn, cur)

    return True, line_nr