from duckduckgo_search import DDGS

class WebPageProvider:
    def __init__(self):
        pass

    def filter_eu_urls(self, url_list):
        return [url for url in url_list if "https://eur-lex.europa.eu/legal-content/EN/TXT/" in url or "https://eur-lex.europa.eu/eli/reg/" in url]

    def get_urls(self, query, max_results=5):
        with DDGS() as ddgs:
            results = [r["href"] for r in ddgs.text(query, max_results=max_results)]
            return results

page_provider = WebPageProvider()
text = """
Council Directive 2008/114/EC of 8 December 2008 on the identification and designation of European critical infrastructures and the 
assessment of the need to improve their  protection (OJ L 345, 23.12.2008, p. 75).
EN Official  Journal  of  the  European  Union 3.6.2022  L  152/47  
"""
urls = page_provider.get_urls("eur-lex.europa" + text)
print(page_provider.filter_eu_urls(urls))
