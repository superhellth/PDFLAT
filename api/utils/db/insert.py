import json
from .base import connect, close
from .getters import get_dataset_model_from_db
from psycopg2.errors import UniqueViolation

def insert_dataframe(table, df):
    # Connect to the database
    conn, cur = connect()

    # generate the query string
    columns = df.columns.tolist()
    placeholder = []
    for c in columns:
        if c == 'nodes':
            placeholder.append('%s::json[]')
        else:
            placeholder.append('%s')

    sql = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join(placeholder)});"

    # Execute the SQL query with the data as parameters
    try:
        for _, row in df.iterrows():

            # use json dumps on all dataframe rows where type is dict
            for i, value in enumerate(row):
                if isinstance(value, dict):
                    row[i] = json.dumps(value)

            cur.execute(sql, row)
    except UniqueViolation as e:
        return False

    close(conn, cur)
    return True

def insert_models(models):
    return insert_dataframe('models', models)

def insert_nodes(nodes):
    return insert_dataframe('nodes', nodes)

def insert_datasets(datasets):
    return insert_dataframe('datasets', datasets)

def insert_pages(pages):
    return insert_dataframe('pages', pages)

def insert_documents(documents):
    return insert_dataframe('documents', documents)

def insert_regions(regions):
    return insert_dataframe('regions', regions)

# special cases

def create_dataset_model(model_id, dataset_id, train_ids, test_ids, eval_ids, num_classes, num_node_features, file_path):
    # Connect to the database
    conn, cur = connect()

    # Define the SQL query to get the data
    sql = """INSERT INTO dataset_models (model_id, dataset_id, train_ids, test_ids, eval_ids, num_classes, num_node_features, file_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""

    # Execute the SQL query with the data as parameters
    cur.execute(sql, (model_id, dataset_id, train_ids, test_ids, eval_ids, num_classes, num_node_features, file_path))

    close(conn, cur)

    return get_dataset_model_from_db(model_id, dataset_id)
