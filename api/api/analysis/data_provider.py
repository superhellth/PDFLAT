import numpy as np
import os
from sklearn import svm
import pickle
from sklearn.model_selection import train_test_split
from api.db.db_reader import DBReader

class DataProvider:
    def __init__(self, dataset_name, data_dir, footnote_label_name="footnote", reference_label_name="reference"):
        self.dataset_name = dataset_name
        self.footnote_label_name = footnote_label_name
        self.reference_label_name = reference_label_name
        self.data_dir = data_dir
        self.data_path = self.data_dir + "vecs.npy"
        self.line_svm_path = self.data_dir + "line_svm.pkl"
        self.char_svm_path = self.data_dir + "char_svm.pkl"
        self.reader = DBReader()
        self.dataset = [dataset for dataset in self.reader.get_all_datasets() if dataset["name"] == self.dataset_name][0]
        self.document_ids = [document["document_id"] for document in self.reader.get_documents_of_dataset(self.dataset["dataset_id"])]
        self.footnote_label_id = [label for label in self.dataset['labels'] if label['name'] == self.footnote_label_name][0]['id']
        self.reference_label_id = [label for label in self.dataset['labels'] if label['name'] == self.reference_label_name][0]['id']

        if not os.path.exists(self.data_dir):
            os.mkdir(self.data_dir)

        if os.path.exists(self.line_svm_path):
            self.line_svm_trained = True
            with open(self.line_svm_path, "rb") as f:
                self.line_svm = pickle.load(f)
        else:
            self.line_svm_trained = False
            self.line_svm = None

        if os.path.exists(self.char_svm_path):
            self.char_svm_trained = True
            with open(self.char_svm_path, "rb") as f:
                self.char_svm = pickle.load(f)
        else:
            self.char_svm_trained = False
            self.char_svm = None

        if os.path.exists(self.data_path):
            self.data_loaded = True
            with open(self.data_path, "rb") as f:
                self.line_labels = np.load(f)
                self.line_vecs = np.load(f)
                self.line_vecs_normed = np.load(f)
                self.char_labels = np.load(f)
                self.char_vecs = np.load(f)
                self.char_vecs_normed = np.load(f)
        else:
            self.data_loaded = False
            self.line_labels = None
            self.char_labels = None
            self.line_vecs = None
            self.char_vecs = None
            self.line_vecs_normed = None
            self.char_vecs_normed = None

    def get_trained_svm(self, type="lines", retrain=False, balance_ratio=4, reload_data=False, run_test=False, test_size=0.33):
        X_train, X_test, y_train, y_test = self.get_splits(type=type, normed=True, test_size=test_size, balance_ratio=balance_ratio, reload_data=reload_data)
        clf = None
        if type == "lines" and self.line_svm_trained and not retrain:
            clf = self.line_svm
        elif type == "chars" and self.char_svm_trained and not retrain:
            clf = self.char_svm
        if not run_test:
            test_size = 0
        if clf is not None:
            self.test_svm(clf, X_test, y_test)
            return clf
        clf = self.train_svm(X_train, X_test, y_train, y_test, run_test=run_test)
        if type == "lines":
            self.line_svm = clf
            path = self.line_svm_path
        elif type == "chars":
            self.char_svm = clf
            path = self.char_svm_path
        with open(path, "wb") as f:
            pickle.dump(clf, f)
        return clf

    def train_svm(self, X_train, X_test, y_train, y_test, run_test=True):
        clf = svm.SVC()
        clf.fit(X_train, y_train)
        if run_test:
            self.test_svm(clf, X_test, y_test)
        return clf
    
    def test_svm(self, clf, X_test, y_test):
        preds = clf.predict(X_test)
        correct_normal = len([1 for i, pred in enumerate(preds) if pred == -1 and y_test[i] == -1])
        correct_foot = len([1 for i, pred in enumerate(preds) if pred == 1 and y_test[i] == 1])
        correct_total = len([1 for i, pred in enumerate(preds) if pred == y_test[i]])
        print(f"Classified {len(preds)} instances.")
        print(f"{correct_normal} correctly classified as negative")
        print(f"{correct_foot} correctly classified as positive")
        print(f"{correct_total} correctly classified")
        print(f"{len(preds) - correct_total} wrongly classified")
        print(f"Of which {len([1 for i, pred in enumerate(preds) if pred != y_test[i] and y_test[i] == 1])} were negatives")

    def get_splits(self, type="lines", normed=True, test_size=0.33, balance_ratio=4, random_state=42, reload_data=False):
        if not self.data_loaded or reload_data:
            self.load_training_data()
        if type == "lines":
            labels = self.line_labels
            vecs = self.line_vecs
            vecs_normed = self.line_vecs_normed
        elif type == "chars":
            labels = self.char_labels
            vecs = self.char_vecs
            vecs_normed = self.char_vecs_normed
        positive_indices = np.where(labels == 1)[0]
        negative_indices = np.where(labels == -1)[0]
        np.random.seed(42)
        selected_negative_indices = np.random.choice(negative_indices, positive_indices.shape[0] * balance_ratio, replace=False)
        selected_indices = np.union1d(selected_negative_indices, positive_indices)

        balanced_vecs = vecs[selected_indices]
        balanced_vecs_normed = vecs_normed[selected_indices]

        if normed:
            return train_test_split(balanced_vecs_normed, labels[selected_indices], test_size=test_size, random_state=random_state)
        else:
            return train_test_split(balanced_vecs, labels[selected_indices], test_size=test_size, random_state=random_state)
        
    def normalize(self, vecs, type="lines"):
        if not self.data_loaded:
            self.load_training_data()
        vecs = np.array(vecs)
        n_vecs = vecs.shape[0]
        if type == "lines":
            vecs = np.concatenate((self.line_vecs, vecs), axis=0)
        elif type == "chars":
            vecs = np.concatenate((self.char_vecs, vecs), axis=0)
        else:
            print("Unknown Type. Choose 'lines' or 'chars'.")
            return None
        return self.norm(vecs)[-n_vecs:]
    
    def norm(self, vecs):
        return np.nan_to_num((vecs - np.mean(vecs, axis=0)) / np.std(vecs, axis=0), nan=0)

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
        self.line_labels = np.array([1 if line.label == self.footnote_label_id else -1 for line in all_lines])
        self.line_vecs = np.array(all_line_vecs)
        self.line_vecs_normed = self.norm(self.line_vecs)
        self.char_labels = np.array([1 if char["label"] == self.reference_label_id else -1 for char in all_chars])
        self.char_vecs = np.array(all_char_vecs)
        self.char_vecs_normed = self.norm(self.char_vecs)
        with open(self.data_path, "wb") as f:
            np.save(f, self.line_labels)
            np.save(f, self.line_vecs)
            np.save(f, self.line_vecs_normed)
            np.save(f, self.char_labels)
            np.save(f, self.char_vecs)
            np.save(f, self.char_vecs_normed)
