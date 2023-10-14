from .base import connect, close

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

def delete_region_from_db(region_id):
    return delete_row_by_id('regions', region_id)

def delete_document_from_db(document_id):
    return delete_row_by_id('documents', document_id)

def delete_dataset_from_db(dataset_id):
    return delete_row_by_id('datasets', dataset_id)

def delete_model_from_db(model_id):
    return delete_row_by_id('models', model_id)

def delete_page_from_db(document_id, page_nr):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = """DELETE FROM pages WHERE document_id = %s AND page_nr = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (document_id, page_nr))

    rowcount = cur.rowcount
    close(conn, cur)

    # check if row was deleted
    if rowcount == 0:
        return False
    return True
    

def remove_label_for_dataset(dataset_id, label):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    # update the labels list of the table by adding the new label
    sql = """UPDATE datasets SET labels = array_remove(labels, %s) WHERE dataset_id = %s;"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (label, dataset_id))

    close(conn, cur)

    return True