class Line:

    def __init__(self, document_id, page_nr, line_nr, x, y, width, height) -> None:
        self.document_id = document_id
        self.page_nr = page_nr
        self.line_nr = line_nr
        self.x = x
        self.y = y
        self.width = width
        self.height = height