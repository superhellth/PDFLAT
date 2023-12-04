import re

class Line:

    def __init__(self, document_id, page_nr, line_nr, text, x, y, width, height, label=None, n_lines_below=None, avg_char_size=None, median_char_size=None, merged=[]) -> None:
        self.document_id = document_id
        self.page_nr = page_nr
        self.line_nr = line_nr
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label = label
        self.summary = ""
        self.keywords = ""
        self.bm25 = ""
        if n_lines_below is not None:
            self.n_lines_below = n_lines_below
            self.avg_char_size = avg_char_size
            self.median_char_size = median_char_size
        else:
            self.n_lines_below = -1
            self.avg_char_size = -1
            self.median_char_size = -1
        self.merged = merged
        self.matches_regex = re.match(r'[(][ ]?\d+[ ]?[)] ', self.text.strip()) is not None and re.match(r'[(][ ]?\d+[ ]?[)] ', self.text.strip()).start() == 0
        self.special_percent = len([c for c in self.text if c.isalpha()]) / len(self.text)

    def merge(self, line, number):
        if self.document_id != line.document_id or self.page_nr != line.page_nr:
            return None
        text = "\n".join([self.text, line.text])
        x = min(self.x, line.x)
        y = min(self.y, line.y)
        width = max([self.x + self.width, line.x + line.width]) - x
        height = max([self.y + self.height, line.y + line.height]) - y
        n_lines_below = min([self.n_lines_below, line.n_lines_below])
        merged = self.merged + line.merged + [self.line_nr, line.line_nr]
        avg_char_size = (self.avg_char_size + line.avg_char_size) / 2
        median_char_size = (self.median_char_size + line.median_char_size) / 2
        return Line(self.document_id, self.page_nr, number, text, x, y, width, height, label=-1, n_lines_below=n_lines_below, avg_char_size=avg_char_size, median_char_size=median_char_size, merged=merged)