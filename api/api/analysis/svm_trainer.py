import numpy as np
from api.analysis.pdf_scanner import PDFScanner
from api.db.db_reader import DBReader

class SVMTrainer:
    def __init__(self, dataset_name, retrain=False, footnote_label_name="footnote", reference_label_name="reference"):
        self.dataset_name = dataset_name
        self.footnote_label_name = footnote_label_name
        self.reference_label_name = reference_label_name
        self.reader = DBReader()
        self.dataset = [dataset for dataset in self.reader.get_all_datasets() if dataset["name"] == self.dataset_name][0]
        self.document_ids = [document["document_id"] for document in self.reader.get_documents_of_dataset(self.dataset["dataset_id"])]
        self.footnote_label_id = [label for label in self.dataset['labels'] if label['name'] == self.footnote_label_name][0]['id']
        self.reference_label_id = [label for label in self.dataset['labels'] if label['name'] == self.reference_label_name][0]['id']

        self.was_trained = False
        self.lines = None
        self.chars = None
        self.line_vecs = None
        self.char_vecs = None

    def train_svm(self, type="lines"):
        pass

    def get_training_data(self, type="lines"):
        if self.lines is None:
            self.load_training_data()
        if type == "lines":
            return self.lines, self.line_vecs
        elif type == "chars":
            return self.chars, self.char_vecs
        else:
            print("Unknown Type. Choose 'lines' or 'chars'.")
            return None
        
    def normalize(self, vecs, type="lines"):
        vecs = np.array(vecs)
        n_vecs = vecs.shape[0]
        if type == "lines":
            vecs = self.line_vecs + vecs
        elif type == "chars":
            vecs = self.char_vecs + vecs
        else:
            print("Unknown Type. Choose 'lines' or 'chars'.")
            return None
        return np.nan_to_num((vecs - np.mean(vecs, axis=0)) / np.std(vecs, axis=0), nan=0)[-n_vecs:]


    def load_training_data(self):
        scanner = PDFScanner()
        all_lines = []
        all_chars = []
        all_line_vecs = []
        all_char_vecs = []
        for document_id in self.document_ids:
            document = self.reader.get_document_as_class(document_id)
            lines, line_vecs = scanner.get_line_features(doc=document)
            all_lines += lines
            all_line_vecs += line_vecs
            chars, char_vecs = scanner.get_char_features(doc=document)
            all_chars += chars
            all_char_vecs += char_vecs
        self.lines = all_lines
        self.line_vecs = all_line_vecs
        self.chars = all_chars
        self.char_vecs = all_char_vecs
        # TODO: Save to file
