import os
import io
import statistics
import pdfplumber
import numpy as np
from bs4 import BeautifulSoup
from api.utils.line import Line
from api.utils.page import Page
from api.utils.document import Document


class PDFScanner:

    def __init__(self):
        pass

    def get_line_features(self, doc=None, doc_path=None):
        if doc_path is not None:
            doc = self.parse_pdf(doc_path)
        line_features_by_page = [
            self.page_lines_to_features(page) for page in doc.pages]
        line_features = [
            line_f for page_line_features in line_features_by_page for line_f in page_line_features]
        lines = [line for page in doc.pages for line in page.lines]
        return lines, line_features

    def page_lines_to_features(self, page):
        page_lines = page.lines
        median_x = statistics.median([line.x for line in page_lines])
        lines_by_y_asc = sorted(page_lines, key=lambda x: x.y)
        line_distances = [lines_by_y_asc[i].y - (lines_by_y_asc[i - 1].y +
                                                 lines_by_y_asc[i - 1].height) for i in range(1, len(lines_by_y_asc))]
        median_line_distance = statistics.median(line_distances)
        # regex match
        return np.array([np.array([median_x, median_line_distance, page.n_horizontal_lines, line.x, line.y, line.width, line.height, line.n_lines_below, len(line.text)]) for line in page_lines])

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
