from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import requests

class WebPageProvider:
    def __init__(self):
        pass

    def get_html_url(self, query, max_considerations=5):
        link_list = self.filter_eu_urls(self.get_urls(query, max_results=max_considerations))
        if link_list == []:
            print("No EUR-Lex URL found.")
            return None
        url = link_list[0]
        if "EN/TXT/HTML" in url:
            return url
        print(f"Accessing: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print("Couldn't access website.")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        refs = [link.get("href") for link in links]
        filtered_refs = [ref for ref in refs if ref is not None and "EN/TXT/HTML" in ref]
        if filtered_refs == []:
            print("No matching URL found.")
            return None
        url = filtered_refs[0]
        parts = url.split("/legal-content/")
        url = "https://eur-lex.europa.eu/legal-content/" + parts[1]
        return url

    def get_text(self, url):
        print(f"Accessing: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            print("Couldn't access website.")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    
    def get_text_from_footnote(self, footnote_text, max_considerations=5):
        html_url = self.get_html_url(footnote_text, max_considerations=max_considerations)
        if html_url is None:
            return None
        else:
            return self.get_text(html_url)

    def filter_eu_urls(self, url_list):
        return [url for url in url_list if "https://eur-lex.europa.eu/legal-content/EN/TXT/?" in url or "https://eur-lex.europa.eu/eli/reg/" in url or "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML" in url]

    def get_urls(self, query, max_results=5):
        with DDGS() as ddgs:
            try:
                results = [r["href"] for r in ddgs.text(query[:500], max_results=max_results)]
            except:
                return []
            return results
