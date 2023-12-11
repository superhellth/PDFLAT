import json
from opensearchpy import OpenSearch

host = 'localhost'
port = 9200
auth = ('admin', 'admin') # For testing only. Don't store credentials in code.

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts = [{'host': host, 'port': port}],
    http_auth = auth,
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
)

files = ["CELEX_32017R1938_EN_TXT", "CELEX_32018R1999_EN_TXT", "CELEX_32019R0941_EN_TXT", "CELEX_32019R0942_EN_TXT", "CELEX_32019R0943_EN_TXT"]

indicies = ["default", "insert", "bm25", "keywords", "summary"]
index_to_free_id = {index: 0 for index in indicies}

for file in files:

    versions = ["default-" + file + ".json", "enriched-" + file + "-insert.json", "enriched-" + file + "-bm25.json", "enriched-" + file + "-kw.json",
                "enriched-" + file + "-summary.json"]

    for i, version in enumerate(versions):
        index = indicies[i]
        with open(version, "r", encoding="utf-8") as f:
            dic_list = json.load(f)
            for page_passages in dic_list:
                for passage in page_passages:
                    document = {
                    'text': passage["text"],
                    'file_name': file,
                    'page': passage["page"]
                    }

                    response = client.index(
                        index = indicies[i],
                        body = document,
                        id = str(index_to_free_id[index]),
                        refresh = True
                    )
                    index_to_free_id[index] += 1
                    print(response)
