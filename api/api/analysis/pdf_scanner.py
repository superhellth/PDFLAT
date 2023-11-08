import os
import io
import statistics
from collections import defaultdict
import pdfplumber
import numpy as np
from bs4 import BeautifulSoup
from api.db.db_reader import DBReader
from api.utils.line import Line
from api.utils.page import Page
from api.utils.document import Document


class PDFScanner:

    def __init__(self):
        self.reader = DBReader()

    def get_line_features(self, doc=None, doc_path=None):
        if doc_path is not None:
            doc = self.parse_pdf(doc_path)
            lines_by_page = self.merge_lines([page.lines for page in doc.pages])
            for i, page in enumerate(doc.pages):
                page.lines = lines_by_page[i]
        line_features_by_page = [
            self.page_lines_to_features(page) for page in doc.pages if len(page.lines) > 1]
        line_features = [
            line_f for page_line_features in line_features_by_page for line_f in page_line_features]
        lines = [line for page in doc.pages for line in page.lines]
        return lines, line_features
    
    def get_char_features(self, doc=None, doc_path=None):
        if doc_path is not None:
            doc = self.parse_pdf(doc_path)
        char_features_by_page = [self.page_chars_to_features(page) for page in doc.pages if len(page.chars) > 1]
        char_features = [char_f for page_char_features in char_features_by_page for char_f in page_char_features]
        chars = [char for page in doc.pages for char in page.chars]
        return chars, char_features
    
    def merge_lines(self, lines_by_page):
        merged_by_page = []
        for page_lines in lines_by_page:
            page_lines_by_y = sorted(page_lines, key=lambda x: x.y, reverse=True)
            if len(page_lines) > 0:
                highest_line_nr = max([line.line_nr for line in page_lines])
            else:
                highest_line_nr = 0
            for t in range(5):
                new_merged = []
                merged_numbers = []
                for i in range(len(page_lines_by_y) - 1):
                    if page_lines_by_y[i].n_lines_below == 0 and page_lines_by_y[i + 1].n_lines_below == 0:
                        if 7 < page_lines_by_y[i].x - page_lines_by_y[i + 1].x < 15:
                                highest_line_nr += 1
                                merged = page_lines_by_y[i + 1].merge(page_lines_by_y[i], highest_line_nr)
                                new_merged.append(merged)
                                merged_numbers += merged.merged
                page_lines_by_y = sorted([line for line in page_lines_by_y if line.line_nr not in merged_numbers] + new_merged, key=lambda x: x.y, reverse=True)
            merged_by_page.append(page_lines_by_y)
        return merged_by_page


    def page_lines_to_features(self, page):
        page_lines = page.lines
        median_x = statistics.median([line.x for line in page_lines])
        lines_by_y_asc = sorted(page_lines, key=lambda x: x.y)
        line_distances = [lines_by_y_asc[i].y - (lines_by_y_asc[i - 1].y +
                                                 lines_by_y_asc[i - 1].height) for i in range(1, len(lines_by_y_asc))]
        median_line_distance = statistics.median(line_distances)
        regex_weight = 10
        return np.array([np.array([regex_weight if line.matches_regex else 0, median_x - line.x, page.median_n_lines_below - line.n_lines_below, page.median_char_size - line.median_char_size, line.y, line.special_percent]) for line in page_lines])

    def page_chars_to_features(self, page):
        page_chars = page.chars
        # print(page_chars)
        median_char_height = statistics.median([char["height"] for char in page_chars])
        median_char_width = statistics.median([char["width"] for char in page_chars])
        bottom_dict = defaultdict(int)
        for char in page_chars:
            if "y" not in char:
                char["y"] = char["top"]
            bottom_dict[int(char["y"] + char["height"])] += 1
        return np.array([np.array([char["width"] - median_char_width, char["height"] - median_char_height, bottom_dict[int(char["y"] + char["height"])]]) for char in page_chars])

    def get_position(self, element):
        """Calculate the position of a given BeautifulSoup element.

        Args:
            element (BF element): Element to extract positional attributes from.

        Returns:
            int[]: x position, y position, width and height.
        """
        return float(element['xMin']), float(element['yMin']), float(element['xMax']) - float(element['xMin']), float(element['yMax']) - float(element['yMin'])

    def parse_pdf(self, doc_path):
        """Extract lines and characters from PDF.

        Args:
            doc_path (str): Path to pdf to parse.

        Returns:
            Document: Converted document.
        """

        # Convert pdf to xml using pdftotext
        xml_path = doc_path.replace('.pdf', '.xml')
        os.system(
            f'pdftotext -bbox-layout {doc_path} {xml_path}')
        file_handler = io.open(xml_path,
                               mode="r", encoding="utf-8").read()
        soup = BeautifulSoup(file_handler, 'lxml-xml')
        doc = soup.find('doc')
        doc_pages = doc.select('page')

        pages = []
        chars_by_page = []

        # Extract chars using PDFPlumber
        with pdfplumber.open(doc_path) as pdf:
            for page_nr, page in enumerate(pdf.pages):
                chars_by_page.append(page.chars)

        # Extract lines using pdftotext
        page_width, page_height = int(np.floor(float(doc_pages[0]['width']))), int(
            np.floor(float(doc_pages[0]['height'])))
        for page_nr, doc_page in enumerate(doc_pages):
            lines = []
            line_objects = doc_page.select('line')
            for line_nr, line_object in enumerate(line_objects):
                # Create line objects ready for db
                x, y, width, height = self.get_position(line_object)
                word_objects = line_object.select('word')
                line_text = " ".join(
                    [word_object.text for word_object in word_objects])
                line = Line(None, page_nr, line_nr,
                            line_text, x, y, width, height)
                lines.append(line)

            # Extract features using PDFPlumber
            with pdfplumber.open(doc_path) as pdf:
                pages.append(Page(None, page_nr, None, page_width,
                                  page_height, lines, chars_by_page[page_nr], pdfplumber_page=pdf.pages[page_nr]))

        return Document(None, None, None, pages)


# scanner = PDFScanner()
# print(scanner.get_line_features(
#     "../../../container_data/data/0fbb77ce73a0e84c4c7ba9268b9bd88b.pdf"))
