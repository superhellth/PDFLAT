import psycopg2
from psycopg2.extras import RealDictCursor

PG_CREDENTIALS = {
    "host": "pg-db",
    "database": "test_db",
    "user": "test_user",
    "password": "PG_PASSWORD"
}


def connect(dicts=False):
    # Connect to the database
    conn = psycopg2.connect(**PG_CREDENTIALS)

    # Open a cursor to perform database operations

    cur = None
    if dicts:
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        cur = conn.cursor()

    return conn, cur


def close(conn, cur):
    # Commit the changes to the database
    conn.commit()

    # Close the cursor and database connection
    cur.close()
    conn.close()