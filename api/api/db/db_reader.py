from db_connection import DBConnection


class DBReader(DBConnection):
    """Class to read from database.

    Args:
        DBConnection (DBConnection): The base connection to the database.
    """

    def __init__(self) -> None:
        DBConnection.__init__(self)


    def get_all_datasets(self):
        return self.get_rows('datasets')

    def get_dataset(self, dataset_id):
        return self.get_row('datasets', ("dataset_id",), (dataset_id,))
    
    def get_document(self, document_id):
        return self.get_row("documents", ("document_id",), (document_id,))
    
    def get_line(self, document_id, page_nr, line_nr):
        return self.get_row("lines", ("document_id", "page_nr", "line_nr"), (document_id, page_nr, line_nr))

    def get_page(self, document_id, page_nr):
        return self.get_row("pages", ("document_id", "page_nr"), (document_id, page_nr))
    
    def get_documents_of_dataset(self, dataset_id):
        return self.get_rows("documents", ("dataset_id",), (dataset_id,))
    
    def get_pages_of_document(self, document_id):
        return self.get_rows("pages", ("document_id",), (document_id,))
    
    def get_lines_of_page(self, document_id, page_nr):
        return self.get_rows("lines", ("document_id", "page_nr"), (document_id, page_nr))

    def get_chars_of_page(self, document_id, page_nr):
        return self.get_rows("chars", ("document_id", "page_nr"), (document_id, page_nr))
    
    def get_highest_line_nr(self, document_id, page_nr):
        conn, cur = self.connect(dicts=True)
        sql = """SELECT MAX(line_nr) from lines WHERE document_id = %s AND page_nr = %s;"""
        cur.execute(sql, (document_id, page_nr))
        highest_number = dict(cur.fetchone())
        self.close(conn, cur)
        return highest_number["max"]

    def get_row(self, table, primary_key_tuple, primary_key_values):
        conn, cur = self.connect()
        where_clause = f"{primary_key_tuple[0]} = %s"
        for i in range(1, len(primary_key_values)):
            where_clause += f"AND {primary_key_tuple[i]} = %s"
        sql = f"SELECT * FROM {table} WHERE {where_clause};"
        cur.execute(sql, primary_key_values)
        row = cur.fetchone()
        self.close(conn, cur)

        if row:
            return dict(row)
        raise Exception(f'No row with primary key {primary_key_values} in table {table}')

    def get_rows(self, table, key_tuple=None, key_values=None):
        conn, cur = self.connect()
        if key_tuple is None or key_values is None:
            sql = f"""SELECT * FROM {table};"""
            cur.execute(sql)
        else:
            where_clause = f"{key_tuple[0]} = %s"
            for i in range(1, len(key_values)):
                where_clause += f"AND {key_tuple[i]} = %s"
            sql = f"SELECT * FROM {table} WHERE {where_clause};"
            cur.execute(sql, key_values)
        res = cur.fetchall()
        self.close(conn, cur)

        if res:
            return [dict(row) for row in list(res)]
        raise Exception(f'No rows with key {key_values} in table {table}')
