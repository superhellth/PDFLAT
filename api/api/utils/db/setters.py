from .base import connect, close
from psycopg2.extras import Json


# update functions

def update_row_by_id(table, id, data):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = f"""UPDATE {table} SET """

    for key, value in data.items():
        sql += f"""{key} = %s, """

    sql = sql[:-2] + f""" WHERE {table[:-1]}_id = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, tuple(data.values()) + (id,))

    rowcount = cur.rowcount
    close(conn, cur)

    # check if row was updated
    if rowcount == 0:
        return False
    return True


# spetial cases

def label_line_in_db(document_id, page_nr, line_nr, label_id):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = """UPDATE lines SET label = %s WHERE document_id = %s AND page_nr = %s and line_nr = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (label_id, document_id, page_nr, line_nr))

    close(conn, cur)

    return True

def label_char_in_db(document_id, page_nr, char_nr, label_id):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = """UPDATE chars SET label = %s WHERE document_id = %s AND page_nr = %s and char_nr = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (label_id, document_id, page_nr, char_nr))

    close(conn, cur)

    return True

def set_label_for_dataset(dataset_id, label):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    # update the labels list of the table by adding the new label
    sql = """UPDATE datasets SET labels = array_append(labels, %s) WHERE dataset_id = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (Json(label), dataset_id))

    close(conn, cur)

    return True