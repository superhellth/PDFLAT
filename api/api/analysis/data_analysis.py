from api.db.db_reader import DBReader
import statistics

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

page = 0
all_lines = reader.get_all_lines(DOCUMENT_ID, page)
without_merged = [line for line in all_lines if line["merged"] == []]
print(f"On page {page}:")
print(f"All lines length: {len(all_lines)}")
print(f"Non-merged lines length: {len(without_merged)}")
footnote_lines = [line for line in without_merged if line["label"] == footnote_label_id]
non_footnote_lines = [line for line in without_merged if not line["label"] == footnote_label_id]
print(f"Number of footnotes: {len(footnote_lines)}")

def page_lines_to_features(page_lines):
    median_x = statistics.median([line["x"] for line in page_lines])
    lines_by_y_asc = sorted(page_lines, key=lambda x: x["y"])
    line_distances = [lines_by_y_asc[i]["y"] - (lines_by_y_asc[i - 1]["y"] + lines_by_y_asc[i - 1]["height"]) for i in range(1, len(lines_by_y_asc))]
    median_line_distance = statistics.median([line_distances])
    return [[median_x, median_line_distance, line["x"], line["y"], line["width"], line["height"]] for line in page_lines]
    
