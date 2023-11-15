import matplotlib.pyplot as plt
import numpy as np
from sklearn.manifold import TSNE
import pandas as pd
import seaborn as sns
from api.analysis.data_provider import DataProvider
from api.analysis.resolver import FootnoteResolver

trainer = DataProvider(dataset_name="BA", data_dir="./data/")
line_svm = trainer.get_trained_svm(type="lines", retrain=False, balance_ratio=4, reload_data=False, run_test=False)
char_svm = trainer.get_trained_svm(type="chars", retrain=False, balance_ratio=3, reload_data=False, run_test=False)

resolver = FootnoteResolver(trainer)
path = "../../../container_data/data/CELEX_32022R0869_EN_TXT.pdf"
tuples_by_page = resolver.resolve_footnotes(path, line_svm, char_svm)

for page, page_list in tuples_by_page.items():
    for tup in page_list:
        print(tup[0].text)
        print("<>")
        print(tup[1])
        print("--------------")

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
