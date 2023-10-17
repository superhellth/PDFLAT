class Line:

    def __init__(self, document_id, page_nr, line_nr, text, x, y, width, height, merged=False) -> None:
        self.document_id = document_id
        self.page_nr = page_nr
        self.line_nr = line_nr
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.merges = False