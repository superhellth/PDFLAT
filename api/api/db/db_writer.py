from api.api.utils.page import Page
from api.db.db_connection import DBConnection
from api.utils.document import Document

class DBWriter(DBConnection):

    def __init__(self) -> None:
        DBConnection.__init__(self)

    def insert_row(self, table, key_tuple, key_values):
        conn, cur = self.connect()
        attribute_list = "(" + ",".join(key_tuple) + ")"
        value_placeholder = ",".join(["%s" for i in range(len(key_tuple))])
        sql = f"INSERT INTO {table} {attribute_list} VALUES ({value_placeholder});"
        cur.execute(sql, key_values)
        self.close(conn, cur)
        return True
    
    def insert_rows(self, table, key_tuple, key_values_list):
        conn, cur = self.connect()
        attribute_list = "(" + ",".join(key_tuple) + ")"
        value_placeholder = ",".join(["%s" for i in range(len(key_tuple))])
        sql = f"INSERT INTO {table} {attribute_list} VALUES ({value_placeholder});"
        cur.executemany(sql, key_values_list)
        self.close(conn, cur)
        return True

    def insert_document(self, document: Document):
        """Insert a document into the database. Including adding the pages, lines and chars
        into the according tables.

        Args:
            document (Document): The document to index.

        Returns:
            bool: Whether or not the insert was successful.
        """
        self.insert_row("documents", ("document_id", "title", "dataset_id"), (document.document_id, document.title, document.dataset_id))
        page_values_list = [(page.document_id, page.page_nr, page.image_path, page.width, page.height) for page in document.pages]
        self.insert_rows("pages", ("document_id", "page_nr", "image_path", "page_width", "page_height"), page_values_list)
        for page in document.pages:
            line_values_list = [(line.document_id, line.page_nr, line.line_nr, line.text, line.x, line.y, line.width, line.height) for line in page.lines]
            self.insert_rows("lines", ("document_id", "page_nr", "line_nr", "line_text", "x", "y", "width", "height"), line_values_list)
            char_values_list = [(page.document_id, page.page_nr, i, char["text"], char["x0"], char["top"], char["width"], char["height"]) for i, char in enumerate(page.chars)]
            self.insert_rows("chars", ("document_id", "page_nr", "char_nr", "char_text", "x", "y", "width", "height"), char_values_list)

        return True

    def delete_document_from_db(self, document_id):
        conn, cur = self.connect()
        self.delete_row("documents", ("document_id",), (document_id))
        self.delete_rows("pages", ("document_id",), (document_id))
        self.delete_rows("lines", ("document_id",), (document_id))
        self.delete_rows("chars", ("document_id",), (document_id))
        self.close(conn, cur)
        return True
    
    def delete_line(self, document_id, page_nr, line_nr):
        return self.delete_row("lines", ("document_id", "page_nr", "line_nr"), (document_id, page_nr, line_nr))

    def delete_char(self, document_id, page_nr, char_nr):
        return self.delete_row("lines", ("document_id", "page_nr", "char_nr"), (document_id, page_nr, char_nr))

    def delete_dataset(self, dataset_id):
        return self.delete_row("datasets", ("dataset_id",), (dataset_id,))
    
    def remove_label_for_dataset(self, dataset_id, label):
        conn, cur = self.connect()
        sql = """UPDATE datasets SET labels = array_remove(labels, %s) WHERE dataset_id = %s;"""
        cur.execute(sql, (label, dataset_id))
        self.close(conn, cur)
        return True

    def delete_row(self, table, primary_key_tuple, primary_key_values):
        conn, cur = self.connect()
        where_clause = f"{primary_key_tuple[0]} = %s"
        for i in range(1, len(primary_key_values)):
            where_clause += f"AND {primary_key_tuple[i]} = %s"
        sql = f"DELETE FROM {table} WHERE {where_clause};"
        cur.execute(sql, primary_key_values)
        rowcount = cur.rowcount
        self.close(conn, cur)

        if rowcount != 0:
            return True
        raise Exception(f'No row with primary key {primary_key_values} in table {table}')
    
    def delete_rows(self, table, key_tuple=None, key_values=None):
        conn, cur = self.connect()
        if key_tuple is None or key_values is None:
            sql = f"""DELETE FROM {table};"""
            cur.execute(sql)
        else:
            where_clause = f"{key_tuple[0]} = %s"
            for i in range(1, len(key_values)):
                where_clause += f"AND {key_tuple[i]} = %s"
            sql = f"DELETE FROM {table} WHERE {where_clause};"
            cur.execute(sql, key_values)
        rowcount = cur.rowcount
        self.close(conn, cur)

        if rowcount != 0:
            return True
        raise Exception(f'No rows with key {key_values} in table {table}')
