from api.analysis.pdf_scanner import PDFScanner
from api.analysis.data_provider import DataProvider
import re

class FootnoteResolver:

    def __init__(self, svm_trainer: DataProvider):
        self.scanner = PDFScanner()
        self.trainer = svm_trainer

    def insert_footnotes(self, blocks_by_page, footnotes_by_page):
        filtered_blocks_by_page = []
        for page, page_blocks in enumerate(blocks_by_page):
            if page in footnotes_by_page:
                page_footnotes = footnotes_by_page[page]
            else:
                page_footnotes = []

            filtered_page_blocks = []
            for block in page_blocks:
                block_contains = self.contains_reference(block["x"], block["y"], block["width"], block["height"], page_footnotes)
                if block_contains != []:
                    for fr in block_contains:
                        block_text = block["text"]
                        footnote_text = fr[0].text
                        match = re.search("( " + fr[1]["text"] + " )", block_text)
                        if match is not None:
                            dot_pos = [index for index, char in enumerate(block_text) if char == '.' and index > match.start()]
                            if dot_pos == []:
                                block["text"] = block_text + "\n" + footnote_text
                            else:
                                block["text"] = block_text[0:dot_pos[0] + 1] + footnote_text + block_text[dot_pos[0] + 1:]
                filtered_page_blocks.append(block)
            filtered_blocks_by_page.append(filtered_page_blocks)
        return filtered_blocks_by_page

    def contains_reference(self, x, y, width, height, fr_pairs):
        contains = []
        for fr in fr_pairs:
            reference = fr[1]
            if x < reference["x0"] < x + width and y < reference["top"] < y + height:
                contains.append(fr)
        return contains

    def resolve_footnotes(self, path_to_pdf, line_svm, char_svm):
        new_chars, new_vecs_char = self.scanner.get_char_features(doc_path=path_to_pdf)
        normed_vecs = self.trainer.normalize(new_vecs_char, type="chars")
        references_by_page = self.extract_references(char_svm, new_chars, normed_vecs)

        new_lines, new_vecs_line = self.scanner.get_line_features(doc_path=path_to_pdf)
        normed_vecs = self.trainer.normalize(new_vecs_line)
        footnotes_by_page = self.extract_footnotes(line_svm, new_lines, normed_vecs)

        return self.connect(footnotes_by_page, references_by_page)

    def connect(self, footnotes_by_page, references_by_page):
        tuples_by_page = {}
        for page, page_footnotes in footnotes_by_page.items():
            page_tuples = []
            for footnote in page_footnotes:
                extracted = self.extract_number(footnote.text)
                if extracted is not None and page in references_by_page:
                    for reference in references_by_page[page]:
                        ref_text = reference["text"]
                        if ref_text == str(extracted): # and abs(reference["top"] - footnote.y) > 10:
                            page_tuples.append((footnote, reference))
                            break
            tuples_by_page[page] = page_tuples
        return tuples_by_page

    def extract_references(self, clf, chars, char_vecs):
        preds = clf.predict(char_vecs)
        references_by_page = {}
        for i, pred in enumerate(preds):
            if pred == 1:
                page_nr = chars[i]["page_number"] - 1
                if page_nr in references_by_page:
                    references_by_page[page_nr].append(chars[i])
                else:
                    references_by_page[page_nr] = [chars[i]]
        return self.merge_reference_chars(references_by_page)
        
    def extract_footnotes(self, clf, lines, line_vecs):
        preds = clf.predict(line_vecs)
        footnotes_by_page = {}
        for i, pred in enumerate(preds):
            if pred == 1 and len(lines[i].text) > 7 and lines[i].matches_regex:
                page_nr = lines[i].page_nr
                if page_nr in footnotes_by_page:
                    footnotes_by_page[page_nr].append(lines[i])
                else:
                    footnotes_by_page[page_nr] = [lines[i]]
        return footnotes_by_page

    def merge_reference_chars(self, references_by_page):
        merged_references_by_page = {}
        for page, page_references in references_by_page.items():
            new_page_references = []
            skip_list = []
            for char in page_references:
                merged = False
                if char in skip_list:
                    continue
                for char1 in page_references:
                    if char != char1 and abs(char["y0"] - char1["y0"]) < 3 and abs(char["x0"] - char1["x0"]) < 7:
                        new_page_references.append(self.merge(char, char1))
                        skip_list.append(char1)
                        merged = True
                if not merged:
                    new_page_references.append(char)
            merged_references_by_page[page] = new_page_references
        return merged_references_by_page

    def extract_number(self, text):
        if not any(char.isdigit() for char in text):
            return None
        start = -1
        end = -1
        for i, char in enumerate(text):
            if char in "0123456789" and start == -1:
                start = i
            if start != -1 and char not in "0123456789":
                end = i
                break
        return int(text[start:min(end, len(text))])

    def merge(self, char1, char2):
        merged_char = {}
        merged_char["x0"] = min([char1["x0"], char2["x0"]])
        merged_char["top"] = min([char1["top"], char2["top"]])
        if char1["x0"] < char2["x0"]:
            text = char1["text"] + char2["text"]
        else:
            text = char2["text"] + char1["text"]
        merged_char["text"] = text
        return merged_char