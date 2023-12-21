import yake
from rank_bm25 import BM25Okapi
import torch
from transformers import AutoTokenizer, AutoModelWithLMHead
from api.web.web_page_provider import WebPageProvider
from collections import defaultdict

class Enricher:

    def __init__(self):
        self.kw_extractor = yake.KeywordExtractor()
        self.t5_tokenizer = AutoTokenizer.from_pretrained('t5-base')
        self.t5 = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)
    
    def enrich(self, footnotes_by_page, mode="kw"):
        weights = defaultdict(float)
        for page_tuples in footnotes_by_page.items():
            page_tuples = page_tuples[1]
            for tuple in page_tuples:
                footnote_line = tuple[0]
                legal_act_text = tuple[3]
                if legal_act_text is not None:
                    ### summary t5
                    if mode == "summary":
                        inputs = self.t5_tokenizer.encode("summarize: " + legal_act_text,
                                                return_tensors='pt',
                                                max_length=512,
                                                truncation=True)
                        summary_ids = self.t5.generate(inputs, max_length=150, min_length=80, length_penalty=5., num_beams=2)
                        summary = self.t5_tokenizer.decode(summary_ids[0])
                        if summary is not None:
                            footnote_line.summary = footnote_line.summary + "\n" + summary
                    ### keyword version
                    if mode == "kw":
                        keywords = self.kw_extractor.extract_keywords(legal_act_text)
                        for kw in keywords:
                            weights[kw[0]] += kw[1]
                        keyword_text = " ".join([keyword[0] for keyword in keywords])
                        footnote_line.keywords = footnote_line.keywords + "\n" + keyword_text
                    ### BM25 version
                    if mode == "bm25":
                        if tuple[2] is not None:
                            corpus = legal_act_text.split("\n\n")
                            tokenized_corpus = [doc.split(" ") for doc in corpus]
                            bm25 = BM25Okapi(tokenized_corpus)
                            tokenized_query = tuple[2]["text"].split(" ")
                            found = bm25.get_top_n(tokenized_query, corpus, n=1)[0]
                            footnote_line.bm25 = footnote_line.bm25 + "\n" + found
                        else:
                            print("No association found:")

        sorted_items = sorted(weights.items(), key=lambda x: x[1])
        # Displaying the sorted items
        for key, value in sorted_items:
            print(f'{key}: {value}')
        return footnotes_by_page