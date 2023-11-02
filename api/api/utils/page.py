class Page:

    def __init__(self, document_id, page_nr, image_path, width, height, lines, chars, pdfplumber_page=None, n_horizontal_lines=None) -> None:
        self.CURVE_TO_LINE_THRESHOLD = 10
        self.document_id = document_id
        self.page_nr = page_nr
        self.image_path = image_path
        self.width = width
        self.height = height
        self.lines = lines
        self.chars = chars
        self.number_lines = len(self.lines)
        self.number_chars = len(self.chars)
        if pdfplumber_page is not None:
            self.raw_page = pdfplumber_page
            self.chars = pdfplumber_page.chars
            self.curves = pdfplumber_page.curves
            self.raw_lines = pdfplumber_page.lines
            self.rects = pdfplumber_page.rects
            self.horizontal_lines = self.find_horizontals()
            self.n_horizontal_lines = len(self.horizontal_lines)
            for line in self.lines:
                line.n_lines_below = self.find_num_lines_below_above_block(line, below=True)
        else:
            self.n_horizontal_lines = n_horizontal_lines

    def find_num_lines_below_above_block(self, line, below=True) -> int:
        """Count the number of lines and horizontal curves that are below or above the given block. For the blocks the values in blocks_by_page_by_top are used.
        If block has no association return -1.

        Args:
            block (TextBlock): Block to consider.
            
            below (bool, optional): If True, find lines below, otherwise find lines above. Defaults to True.

        Returns:
            int: Number of lines above(if below false) or below(if below true) the given block.
        """
        lines_below_above = 0
        for h_line in self.horizontal_lines:
            # if line["x1"] - line["x0"] > self.width * 0.3:
            if below and line.y + line.height < h_line["top"]:
                lines_below_above += 1
            elif (not below) and line.y + line.height > h_line["top"]:
                lines_below_above += 1
        return lines_below_above

    def find_horizontals(self):
        """
        Find curves and lines that are horizontal, as those are the only ones of relevance. Determined by aspect ratio.
        """
        horizontals = []
        for curve in self.curves + self.raw_lines + self.rects:
            if curve["width"] > curve["height"] * self.CURVE_TO_LINE_THRESHOLD:
                horizontals.append(curve)
        return horizontals