import matplotlib.pyplot as plt
import numpy as np
import yake
from rank_bm25 import BM25Okapi
from sklearn.manifold import TSNE
import pandas as pd
import seaborn as sns
from api.analysis.data_provider import DataProvider
from api.analysis.resolver import FootnoteResolver
from api.analysis.pdf_scanner import PDFScanner
from api.web.web_page_provider import WebPageProvider

print("Training Classifiers...")
trainer = DataProvider(dataset_name="BA", data_dir="./data/")
line_svm = trainer.get_trained_svm(type="lines", retrain=False, balance_ratio=4, reload_data=False, run_test=False)
char_svm = trainer.get_trained_svm(type="chars", retrain=False, balance_ratio=3, reload_data=False, run_test=False)

resolver = FootnoteResolver(trainer)
path = "../../../container_data/data/CELEX_32020R0740_EN_TXT.pdf"
scanner = PDFScanner()
print("Processing pdf...")
raw_blocks = scanner.pdf_to_blocks(path)

with open("./log.txt", "w", encoding="utf-8") as f:
    f.write(str(raw_blocks))

print("Resolving footnotes...")
tuples_by_page = resolver.resolve_footnotes(path, line_svm, char_svm)

print("Enriching footnotes...")
page_provider = WebPageProvider()
kw_extractor = yake.KeywordExtractor()
for page_tuples in tuples_by_page.items():
    page_tuples = page_tuples[1]
    for tuple in page_tuples:
        footnote_line = tuple[0]
        legal_act_text = page_provider.get_text_from_footnote(footnote_line.text)
        if legal_act_text is not None:
            ### keyword version
            # keywords = kw_extractor.extract_keywords(legal_act_text)
            # keyword_text = " ".join([keyword[0] for keyword in keywords])
            # footnote_line.text = keyword_text
            ### BM25 version
            corpus = legal_act_text.split("\n\n")
            tokenized_corpus = [doc.split(" ") for doc in corpus]
            bm25 = BM25Okapi(tokenized_corpus)
            tokenized_query = footnote_line.text.split(" ")
            print("-------------")
            print(footnote_line.text)
            found = bm25.get_top_n(tokenized_query, corpus, n=1)[0]
            print()
            print(found)
            footnote_line.text = found

enriched_blocks = resolver.insert_footnotes(raw_blocks, tuples_by_page)
with open("./log.txt", "a", encoding="utf-8") as f:
    f.write("\n\n")
    f.write(str(enriched_blocks))

# for page, page_list in tuples_by_page.items():
#     for tup in page_list:
#         print(tup[0].text)
#         print("<>")
#         print(tup[1])
#         print("--------------")



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
