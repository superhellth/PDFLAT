class Line:

    def __init__(self, document_id, page_nr, line_nr, text, x, y, width, height, label=None, n_lines_below=None, merged=None) -> None:
        self.document_id = document_id
        self.page_nr = page_nr
        self.line_nr = line_nr
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        if n_lines_below is not None:
            self.n_lines_below = n_lines_below
        else:
            self.n_lines_below = -1
        self.merged = merged