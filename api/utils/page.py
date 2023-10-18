class Page:

    def __init__(self, document_id, page_nr, image_path, width, height, lines, chars) -> None:
        self.document_id = document_id
        self.page_nr = page_nr
        self.image_path = image_path
        self.width = width
        self.height = height
        self.lines = lines
        self.number_lines = len(self.lines)
        self.chars = chars
        self.number_chars = len(self.chars)

