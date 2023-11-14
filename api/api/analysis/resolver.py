from api.analysis.pdf_scanner import PDFScanner


class FootnoteResolver:

    def __init__(self):
        self.scanner = PDFScanner()

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
        return references_by_page
        
    def extract_footnotes(self, clf, lines, line_vecs):
        preds = clf.predict(line_vecs)
        footnotes_by_page = {}
        for i, pred in enumerate(preds):
            if pred == 1 and len(lines[i].text) > 7 and lines[i].matches_regex:
                page_nr = lines[i].page_nr
                print(lines[i].text)
                if page_nr in footnotes_by_page:
                    footnotes_by_page[page_nr].append(lines[i])
                else:
                    footnotes_by_page[page_nr] = [lines[i]]
        return footnotes_by_page

    def connect(self, footnotes, references):
        pass

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