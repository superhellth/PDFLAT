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

q = 'paris agreement'

query = {
  'size': 5,
  'query': {
    'match': {
      'text': q
    }
  }
}

for index in ["default", "insert", "bm25", "keywords", "summary"]:

    response = client.search(
        body = query,
        index = index
    )
    results = response["hits"]["hits"]
    print("=========================================")
    print("=========================================")
    print("=========================================")
    print(f"Index: {results[0]['_index']}")
    print()
    for hit in results:
        print("-------------------------------------")
        source = hit["_source"]
        print(f"Score: {hit['_score']}\n Text: {source['text']}")