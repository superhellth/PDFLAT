import psycopg2
from psycopg2.extras import RealDictCursor


class DBConnection:

    def __init__(self) -> None:
        self.PG_CREDENTIALS = {
            # "host": "pg-db",
            "port": 6543,
            "database": "test_db",
            "user": "test_user",
            "password": "PG_PASSWORD"
        }

    def connect(self):
        """Connect to the database specified in credentials.

        Returns:
            any, any: Connection and Cursor.
        """

        # Connect to the database
        conn = psycopg2.connect(**self.PG_CREDENTIALS)

        # Open a cursor to perform database operations
        cur = conn.cursor(cursor_factory=RealDictCursor)

        return conn, cur

    def close(conn, cur):
        """Commit changes and close connection to database.

        Args:
            conn (any): Database connection.
            cur (any): Database cursor.
        """

        # Commit the changes to the database
        conn.commit()

        # Close the cursor and database connection
        cur.close()
        conn.close()