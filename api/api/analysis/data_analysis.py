import json
import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE
import pandas as pd
import seaborn as sns
from sklearn import svm
from sklearn.model_selection import train_test_split
from api.db.db_reader import DBReader
from api.analysis.pdf_scanner import PDFScanner

DATASET_NAME = "BA"
FOOTNOTE_LABEL_NAME = "footnote"
REFERENCE_LABEL_NAME = "reference"
reader = DBReader()
dataset = [dataset for dataset in reader.get_all_datasets() if dataset["name"] == DATASET_NAME][0]
documents = [document["document_id"] for document in reader.get_documents_of_dataset(dataset["dataset_id"])]

print(f"Dataset ID: {dataset['dataset_id']}")
print(f"Dataset name: {dataset['name']}")
labels = dataset["labels"]
footnote_label_id = [label for label in labels if label['name'] == FOOTNOTE_LABEL_NAME][0]['id']
reference_label_id = [label for label in labels if label['name'] == REFERENCE_LABEL_NAME][0]['id']
print(f"Footnote label ID: {footnote_label_id}")
print(f"Documents:")
print(documents)
print()

pages = 0
lines_by_page_by_doc = []
for document_id in documents:
    n_pages = len(reader.get_all_pages(document_id))
    lines_by_page = []
    for page in range(n_pages):
        all_lines = reader.get_all_lines(document_id, page)
        used_in_merges = []
        for line in all_lines:
            used_in_merges += line["merged"]
        without_merged = [line for line in all_lines if line["line_nr"] not in used_in_merges]
        footnote_lines = [line for line in without_merged if line["label"] == footnote_label_id]
        pages += 1
        lines_by_page.append(without_merged)
    lines_by_page_by_doc.append(lines_by_page)
print(f"Data from {pages} pages")

def normalize_3(embeddings):
    return np.nan_to_num((embeddings - np.mean(embeddings, axis=0)) / np.std(embeddings, axis=0), nan=0)

def tsneplot(lines, embeddings, footnote_label_id):
    embs = np.empty((0, 8), dtype="f")
    word_labels = [line.text[:10] for line in lines]
    color_list = ["green" if line.label == footnote_label_id else "red" for line in lines]

    # adds the vector for each of the closest words to the array
    for emb in embeddings:
        embs = np.append(embs, [emb], axis=0)

    np.set_printoptions(suppress=True)
    Y = TSNE(n_components=2, learning_rate=200, random_state=42,
                perplexity=len(lines) - 5, init="random").fit_transform(embs)

    # sets everything up to plot
    df = pd.DataFrame({"x": [x for x in Y[:, 0]],
                        "y": [y for y in Y[:, 1]],
                        "words": word_labels,
                        "color": color_list})

    fig, _ = plt.subplots()
    fig.set_size_inches(10, 10)

    # basic plot
    p1 = sns.regplot(data=df,
                        x="x",
                        y="y",
                        fit_reg=False,
                        marker="o",
                        scatter_kws={"s": 40, "facecolors": df["color"]}
                        )

    # adds annotations one by one with a loop
    for line in range(0, df.shape[0]):
        p1.text(df["x"][line],
                df["y"][line],
                "  " + df["words"][line].title(),
                horizontalalignment="left",
                verticalalignment="bottom", size="medium",
                color=df["color"][line],
                weight="normal"
                ).set_size(15)

    plt.xlim(Y[:, 0].min() - 50, Y[:, 0].max() + 50)
    plt.ylim(Y[:, 1].min() - 50, Y[:, 1].max() + 50)

    plt.title("t-SNE visualization")
    plt.show()

def normalize(embeddings):
    return np.nan_to_num((embeddings - np.mean(embeddings, axis=0)) / np.std(embeddings, axis=0), nan=0)

def merge_chars(char1, char2):
    merged_char = {}
    merged_char["x0"] = min([char1["x0"], char2["x0"]])
    merged_char["top"] = min([char1["top"], char2["top"]])
    if char1["x0"] < char2["x0"]:
        text = char1["text"] + char2["text"]
    else:
        text = char2["text"] + char1["text"]
    merged_char["text"] = text
    return merged_char

def extract_number(text):
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

scanner = PDFScanner()
labeled_lines = []
labeled_vecs_line = []
for document in documents:
    lines, vecs = scanner.get_line_features(doc=reader.get_document_as_class(document))
    labeled_lines += lines
    labeled_vecs_line += vecs
n_labeled = len(labeled_vecs_line)
new_lines, new_vecs_line = scanner.get_line_features(doc_path="../../../container_data/data/CELEX_32022R0869_EN_TXT.pdf")
all_vecs_line = labeled_vecs_line + new_vecs_line
all_normed_line = normalize(all_vecs_line)
labeled_vecs_line = all_normed_line[0:n_labeled]
new_vecs_line = all_normed_line[n_labeled:]

# balance classes
footnote_indices = [i for i, line in enumerate(labeled_lines) if line.label == footnote_label_id]
normal_indices = [i for i, line in enumerate(labeled_lines) if line.label != footnote_label_id]
selected_normal_indices = np.random.choice(normal_indices, len(footnote_indices) * 4, replace=False)
selected_indices = np.union1d(selected_normal_indices, footnote_indices)

labeled_vecs_line = [labeled_vecs_line[i] for i in selected_indices]
labeled_lines = [labeled_lines[i] for i in selected_indices]

X_train, X_test, y_train, y_test = train_test_split(labeled_vecs_line, [1 if line.label == footnote_label_id else -1 for line in labeled_lines], test_size=0.33, random_state=42)
clf = svm.SVC()
clf.fit(X_train, y_train)
preds = clf.predict(X_test)
correct_normal = len([1 for i, pred in enumerate(preds) if pred == -1 and y_test[i] == -1])
correct_foot = len([1 for i, pred in enumerate(preds) if pred == 1 and y_test[i] == 1])
correct_total = len([1 for i, pred in enumerate(preds) if pred == y_test[i]])
print(f"Classified {len(preds)} / {len(labeled_vecs_line)} lines.")
print(f"{correct_normal} correctly classified as non-foot")
print(f"{correct_foot} correctly classified as foot")
print(f"{correct_total} correctly classified")
print(f"{len(preds) - correct_total} wrongly classified")
print(f"Of which {len([1 for i, pred in enumerate(preds) if pred != y_test[i] and y_test[i] == 1])} were footnotes")

preds = clf.predict(new_vecs_line)
footnotes_by_page = {}
for i, pred in enumerate(preds):
    if pred == 1 and len(new_lines[i].text) > 7 and new_lines[i].matches_regex:
        page_nr = new_lines[i].page_nr
        if page_nr in footnotes_by_page:
            footnotes_by_page[page_nr].append(new_lines[i])
        else:
            footnotes_by_page[page_nr] = [new_lines[i]]

print(len(footnotes_by_page.items()))
# tsneplot(new_lines[:400], new_vecs[:400], footnote_label_id)

labeled_chars = []
labeled_vecs_char = []
for document in documents:
    chars, vecs = scanner.get_char_features(doc=reader.get_document_as_class(document))
    labeled_chars += chars
    labeled_vecs_char += vecs
n_labeled = len(labeled_vecs_char)
new_chars, new_vecs_char = scanner.get_char_features(doc_path="../../../container_data/data/CELEX_32022R0869_EN_TXT.pdf")
all_vecs_char = labeled_vecs_char + new_vecs_char
all_normed_char = normalize(all_vecs_char)
labeled_vecs_char = all_normed_char[0:n_labeled]
new_vecs_char = all_normed_char[n_labeled:]

# balance classes
reference_indices = [i for i, char in enumerate(labeled_chars) if char["label"] == reference_label_id]
normal_indices = [i for i, char in enumerate(labeled_chars) if char["label"] != reference_label_id]
selected_normal_indices = np.random.choice(normal_indices, len(reference_indices) * 3, replace=False)
selected_indices = np.union1d(selected_normal_indices, reference_indices)

labeled_vecs_char = [labeled_vecs_char[i] for i in selected_indices]
labeled_chars = [labeled_chars[i] for i in selected_indices]

X_train, X_test, y_train, y_test = train_test_split(labeled_vecs_char, [1 if char["label"] == reference_label_id else -1 for char in labeled_chars], test_size=0.33, random_state=42)
clf_char = svm.SVC()
clf_char.fit(X_train, y_train)
preds = clf_char.predict(X_test)
correct_normal = len([1 for i, pred in enumerate(preds) if pred == -1 and y_test[i] == -1])
correct_foot = len([1 for i, pred in enumerate(preds) if pred == 1 and y_test[i] == 1])
correct_total = len([1 for i, pred in enumerate(preds) if pred == y_test[i]])
print(f"Classified {len(preds)} / {len(labeled_vecs_char)} chars.")
print(f"{correct_normal} correctly classified as non-reference")
print(f"{correct_foot} correctly classified as reference")
print(f"{correct_total} correctly classified")
print(f"{len(preds) - correct_total} wrongly classified")
print(f"Of which {len([1 for i, pred in enumerate(preds) if pred != y_test[i] and y_test[i] == 1])} were references")

preds = clf_char.predict(new_vecs_char)
references_by_page = {}
for i, pred in enumerate(preds):
    if pred == 1:
        page_nr = new_chars[i]["page_number"] - 1
        if page_nr in references_by_page:
            references_by_page[page_nr].append(new_chars[i])
        else:
            references_by_page[page_nr] = [new_chars[i]]

with open("./log.txt", "w", encoding="utf-8") as f:
    f.write(json.dumps(references_by_page))

# merge references
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
                new_page_references.append(merge_chars(char, char1))
                skip_list.append(char1)
                merged = True
        if not merged:
            new_page_references.append(char)
    merged_references_by_page[page] = new_page_references

with open("./log.txt", "a", encoding="utf-8") as f:
    f.write("\n\n")
    f.write(json.dumps(merged_references_by_page))

tuples_by_page = {}
for page, page_footnotes in footnotes_by_page.items():
    page_tuples = []
    print("------------------")
    print(f"Page: {page}")
    for footnote in page_footnotes:
        print("Footnote:")
        print(footnote.text)
        extracted = extract_number(footnote.text)
        if extracted is not None and page in merged_references_by_page:
            print("References:")
            print(merged_references_by_page[page])
            for reference in merged_references_by_page[page]:
                ref_text = reference["text"]
                if ref_text == str(extracted) and abs(reference["top"] - footnote.y) > 10:
                    page_tuples.append((footnote, reference))
                    break
    tuples_by_page[page] = page_tuples

for page, page_list in tuples_by_page.items():
    for tup in page_list:
        print(tup[0].text)
        print("<>")
        print(tup[1])
        print("--------------")
