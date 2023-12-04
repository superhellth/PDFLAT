import yake
from rank_bm25 import BM25Okapi
import torch
from transformers import AutoTokenizer, AutoModelWithLMHead
from api.web.web_page_provider import WebPageProvider

class Enricher:

    def __init__(self):
        self.kw_extractor = yake.KeywordExtractor()
        self.t5_tokenizer = AutoTokenizer.from_pretrained('t5-base')
        self.t5 = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)
    
    def enrich(self, footnotes_by_page, mode="kw"):
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
                            footnote_line.text = summary
                    ### keyword version
                    if mode == "kw":
                        keywords = self.kw_extractor.extract_keywords(legal_act_text)
                        keyword_text = " ".join([keyword[0] for keyword in keywords])
                        footnote_line.text = keyword_text
                    ### BM25 version
                    if mode == "bm25":
                        corpus = legal_act_text.split("\n\n")
                        tokenized_corpus = [doc.split(" ") for doc in corpus]
                        bm25 = BM25Okapi(tokenized_corpus)
                        tokenized_query = tuple[2].split(" ")
                        found = bm25.get_top_n(tokenized_query, corpus, n=1)[0]
                        footnote_line.text = found
        return footnotes_by_page