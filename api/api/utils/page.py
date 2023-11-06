import re
import numpy as np

class Page:

    def __init__(self, document_id, page_nr, image_path, width, height, lines, chars, pdfplumber_page=None, n_horizontal_lines=None, avg_char_size=None, median_char_size=None) -> None:
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
            if len(self.chars) > 0:
                self.avg_char_size = np.sum([char["size"] for char in self.chars]) / len(self.chars)
                self.median_char_size = [char["size"] for char in self.chars][int(len(self.chars) / 2)]
            else:
                self.avg_char_size = 0
                self.median_char_size = 0
            self.curves = pdfplumber_page.curves
            self.raw_lines = pdfplumber_page.lines
            self.rects = pdfplumber_page.rects
            self.horizontal_lines = self.find_horizontals()
            self.n_horizontal_lines = len(self.horizontal_lines)
            lines_below_list = []
            for line in self.lines:
                n_lines_below = self.find_num_lines_below_above_block(line, below=True)
                line.n_lines_below = n_lines_below
                lines_below_list.append(n_lines_below)
            if len(lines_below_list) > 0:
                self.median_n_lines_below = lines_below_list[int(len(lines_below_list) / 2)]
            else:
                self.median_n_lines_below = 0
            self.associate_blocks()
        else:
            lines_below_list = []
            for line in self.lines:
                lines_below_list.append(line.n_lines_below)
            if len(lines_below_list) > 0:
                self.median_n_lines_below = lines_below_list[int(len(lines_below_list) / 2)]
            else:
                self.median_n_lines_below = 0
            self.n_horizontal_lines = n_horizontal_lines
            self.avg_char_size = avg_char_size
            self.median_char_size = median_char_size

    def associate_blocks(self) -> None:
        """
        For every pdftotext block of the document find groups of pdfplumber chars that could correspond to the block.
        """
        for line in self.lines:
            # replace newlines and whitespaces with \s*
            search_str = re.escape(line.text).replace(
                "\n", r"\s*").replace(r"\\s*", r"\s*").replace(r"\ ", r"\s*")
            candidates = self.raw_page.search(
                search_str, regex=True, case=True)
            
            if len(candidates) > 1:
                candidates = sorted(candidates, key=lambda candidate: abs(candidate["x0"] - line.x) + abs(candidate["top"] - line.y))[0:1]
            if candidates != []:
                avg_char_size = 0
                char_size_list = []
                for char in candidates[0]["chars"]:
                    char_size_list.append(char["size"])
                line.avg_char_size = avg_char_size / len(candidates[0]["chars"])
                line.median_char_size = char_size_list[int(len(char_size_list) / 2)]


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