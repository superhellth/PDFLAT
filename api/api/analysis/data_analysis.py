import statistics
import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE
import pandas as pd
import seaborn as sns
from api.db.db_reader import DBReader

DATASET_NAME = "BA"
FOOTNOTE_LABEL_NAME = "footnote"
DOCUMENT_ID = "fb5e678859ded202b0c7588ffd9e3c21"

reader = DBReader()
dataset = [dataset for dataset in reader.get_all_datasets() if dataset["name"] == "BA"][0]
print(f"Dataset ID: {dataset['dataset_id']}")
print(f"Dataset name: {dataset['name']}")
labels = dataset["labels"]
footnote_label_id = [label for label in labels if label['name'] == FOOTNOTE_LABEL_NAME][0]['id']
print(f"Footnote label ID: {footnote_label_id}")
print()

# page = 0
lines_by_page = []
for page in range(58):
    all_lines = reader.get_all_lines(DOCUMENT_ID, page)
    used_in_merges = []
    for line in all_lines:
        used_in_merges += line["merged"]
    without_merged = [line for line in all_lines if line["line_nr"] not in used_in_merges]
    lines_by_page.append(without_merged)
    # print(f"On page {page}:")
    # print(f"All lines length: {len(all_lines)}")
    # print(f"Non-merged lines length: {len(without_merged)}")
    # footnote_lines = [line for line in without_merged if line["label"] == footnote_label_id]
    # non_footnote_lines = [line for line in without_merged if not line["label"] == footnote_label_id]
    # print(f"Number of footnotes: {len(footnote_lines)}")

def page_lines_to_features(page_lines):
    median_x = statistics.median([line["x"] for line in page_lines])
    lines_by_y_asc = sorted(page_lines, key=lambda x: x["y"])
    line_distances = [lines_by_y_asc[i]["y"] - (lines_by_y_asc[i - 1]["y"] + lines_by_y_asc[i - 1]["height"]) for i in range(1, len(lines_by_y_asc))]
    median_line_distance = statistics.median(line_distances)
    return np.array([np.array([median_x, median_line_distance, line["x"], line["y"], line["width"], line["height"]]) for line in page_lines])
    
def normalize_data(embeddings):
    avg = np.sum(embeddings, axis=0) / embeddings.shape[0]
    normalized = embeddings - avg
    final = normalized / np.max(np.abs(normalized), axis=0)
    final = np.nan_to_num(final)
    return final

def normalize_2(embeddings):
    return (embeddings - np.mean(embeddings)) / np.std(embeddings)

def normalize_3(embeddings):
    return np.nan_to_num((embeddings - np.mean(embeddings, axis=0)) / np.std(embeddings, axis=0), nan=0)

def tsneplot(lines, embeddings):
    embs = np.empty((0, 6), dtype="f")
    word_labels = ["" for line in lines]
    color_list = ["green" if line["label"] == 6 else "red" for line in lines]

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

embeddings_by_page = [page_lines_to_features(page_lines) for page_lines in lines_by_page]
all_normalized = normalize_3([line_f for page_features in embeddings_by_page for line_f in page_features])
all_lines = [line for page_lines in lines_by_page for line in page_lines]
# print(all_lines)
# embeddings = page_lines_to_features(without_merged)
# normalized = normalize_3(embeddings)
tsneplot(all_lines, all_normalized)