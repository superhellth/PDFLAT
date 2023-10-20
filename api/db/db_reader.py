from db.db_connection import DBConnection


class DBReader(DBConnection):

    def __init__(self) -> None:
        DBConnection.__init__(self)


    def get_all_datasets(self):
        return self.get_all_rows('datasets')


    def get_dataset_by_id(self, dataset_id):
        return self.get_row_by_id('datasets', dataset_id)


    def get_page_from_db(self, document_id, page_nr):
        conn, cur = self.connect(dicts=True)
        sql = """SELECT * FROM pages WHERE document_id = %s AND page_nr = %s;"""
        cur.execute(sql, (document_id, page_nr))
        page = cur.fetchone()
        self.close(conn, cur)

        if page:
            return page
        raise Exception(f'No page with id {page_nr} in table pages')


    def get_row_by_primary_key(self, table, primary_key_tuple, primary_key_values):
        conn, cur = self.connect()
        where_clause = f"{primary_key_tuple[0]} = %s"
        for i in range(1, len(primary_key_values)):
            where_clause += f"AND {primary_key_tuple[i]} = %s"
        sql = f"SELECT * FROM {table} WHERE {where_clause};"
        cur.execute(sql, primary_key_values)
        row = cur.fetchone()
        self.close(conn, cur)

        if row:
            return row
        raise Exception(f'No row with primary key {primary_key_values} in table {table}')


    def get_all_rows(self, table):
        conn, cur = self.connect(dicts=True)
        sql = f"""SELECT * FROM {table};"""
        cur.execute(sql)
        rows = list(cur.fetchall())
        self.close(conn, cur)

        return rows
