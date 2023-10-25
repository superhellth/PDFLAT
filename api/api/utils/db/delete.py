from .base import connect, close
import json

# delete_by_id functions
def delete_row_by_id(table, id):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = f"""DELETE FROM {table} WHERE {table[:-1]}_id = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (id,))

    rowcount = cur.rowcount
    close(conn, cur)

    # check if row was deleted
    if rowcount == 0:
        return False
    return True

def delete_dataset_from_db(dataset_id):
    return delete_row_by_id('datasets', dataset_id)

def delete_document_from_db(document_id):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = """DELETE FROM documents WHERE document_id = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (document_id,))
    rowcount = cur.rowcount

    sql = """DELETE FROM pages WHERE document_id = %s;"""
    cur.execute(sql, (document_id,))
    rowcount += cur.rowcount

    sql = """DELETE FROM lines WHERE document_id = %s;"""
    cur.execute(sql, (document_id,))
    rowcount += cur.rowcount

    sql = """DELETE FROM chars WHERE document_id = %s;"""
    cur.execute(sql, (document_id,))
    rowcount += cur.rowcount
    
    close(conn, cur)

    # check if row was deleted
    if rowcount == 0:
        return False
    return True

def delete_page_from_db(document_id, page_nr):
    conn, cur = connect()
    sql = """DELETE FROM pages WHERE document_id = %s AND page_nr = %s;"""
    cur.execute(sql, (document_id, page_nr))
    rowcount = cur.rowcount

    sql = """DELETE FROM lines WHERE document_id = %s AND page_nr = %s;"""
    cur.execute(sql, (document_id, page_nr))
    rowcount += cur.rowcount

    sql = """DELETE FROM chars WHERE document_id = %s AND page_nr = %s;"""
    cur.execute(sql, (document_id, page_nr))
    rowcount += cur.rowcount

    close(conn, cur)
    if rowcount == 0:
        return False
    return True

def delete_line_from_db(document_id, page_nr, line_nr):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = """DELETE FROM lines WHERE document_id = %s AND page_nr = %s AND line_nr = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (document_id, page_nr, line_nr))
    rowcount = cur.rowcount
    
    close(conn, cur)

    # check if row was deleted
    if rowcount == 0:
        return False
    return True

def delete_char_from_db(document_id, page_nr, char_nr):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = """DELETE FROM chars WHERE document_id = %s AND page_nr = %s AND char_nr = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (document_id, page_nr, char_nr))
    rowcount = cur.rowcount
    
    close(conn, cur)

    # check if row was deleted
    if rowcount == 0:
        return False
    return True

def remove_label_for_dataset(dataset_id, label_json, label):
    # Connect to the database
    conn, cur = connect()
    print(label)

    # Define the SQL query to get the data
    # update the labels list of the table by adding the new label
    sql = """UPDATE datasets SET labels = array_remove(labels, %s) WHERE dataset_id = %s;"""
    # Execute the SQL query with the data as parameters
    cur.execute(sql, (label_json, dataset_id))
    sql = """UPDATE lines SET label = -1 WHERE label = %s"""
    cur.execute(sql, (label["id"],))
    sql = """UPDATE chars SET label = -1 WHERE label = %s"""
    cur.execute(sql, (label["id"],))

    close(conn, cur)

    return True