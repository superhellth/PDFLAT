from collections import defaultdict
# import matplotlib.pyplot as plt
# import seaborn as sns
# from duckduckgo_search import DDGS

# query = """test"""
with open("kw.txt", "r", encoding="utf-8") as f:
    lines = f.read()

lines = lines.split("\n")
tuples = [(line.split(": ")[0], float(line.split(": ")[1])) for line in lines]
weights = defaultdict(float)
for t in tuples:
    weights[t[0]] += t[1]

sorted_items = sorted(weights.items(), key=lambda x: x[1])
most_frequent_kw = [item[0] for item in sorted_items]
print([i for i in reversed(most_frequent_kw)])
# with DDGS() as ddgs:
#     duckduckgo_res = [r["href"] for r in ddgs.text(query, safesearch='off', timelimit='y', max_results=10)]
# print(duckduckgo_res)
    # google_res = [url for url in search(query[:500], tld="co.in", num=max_results, stop=max_results)]
# def plot_confusion_matrix(tp, fp, fn, tn, classes, title="Confusion Matrix"):
#     # Create confusion matrix
#     cm = [[tp, fp], [fn, tn]]
    
#     # Plot the confusion matrix
#     plt.figure(figsize=(6, 4))
#     sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
#     plt.xlabel('Predicted')
#     plt.ylabel('True')
#     plt.title(title)
#     plt.show()

# plot_confusion_matrix(67, 1, 0, 229, classes=("Positive", "Negative"), title="Reference Prediction")