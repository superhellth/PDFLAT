import numpy as np
from opensearchpy import OpenSearch

host = 'localhost'
port = 9200
auth = ('admin', 'admin')  # For testing only. Don't store credentials in code.

# Create the client with SSL/TLS enabled, but hostname verification disabled.
client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=False,
    ssl_assert_hostname=False,
    ssl_show_warn=False
)

q = 'system operator'

queries = "European Union.EUROPEAN PARLIAMENT.Member States.European.European Union.Emissions.global.market-based.measure.Article.Union.ICAO.global market-based.Paris Agreement.European Council.emissions.Commission.ICAO.Single European.Sky.COUNCIL.market-based measure.global market-based.Commission Regulation.ICAO global".split(
    ".")
queries2 = "transmission.system.operators.transmission system.system operators.Article.system transmission.gas.transmission systems.network.COMMISSION.gas network.users.ENTSO.for Gas.gas transmission networks.storage system operators.operators Agency.capacity.gas transmission.natural gas transmission.operator".split(
    ".")

# Generate 10 information retrieval example queries using keywords on the topic of energy politics in the EU with a special focus on these 5 topics:
# measures  to  safeguard  the  security  of  gas  supply,
# he  Governance  of  the  Energy  Union  and  Climate  Action, 
# risk-preparedness in the electricity sector,
# establishing a European Union Agency for the Cooperation of Energy Regulators,
# on the internal market for electricity 
queries3 = ["EU gas supply security measures 2023",
            "Energy Union and Climate Action governance in the EU",
            "Electricity sector risk-preparedness policies in the European Union",
            "Role of the European Union Agency for the Cooperation of Energy Regulators in energy politics",
            "Internal market for electricity regulations in the EU",
            "Recent developments in EU energy politics: safeguarding gas supply",
            "Challenges and strategies for ensuring electricity sector risk-preparedness in the European Union",
            "Governance framework of the Energy Union and Climate Action in the EU",
            "Impact of the European Union Agency for the Cooperation of Energy Regulators on energy market integration",
            "Assessment of internal market dynamics in the EU for electricity in 2023"]
indicies = ["default", "insert", "bm25", "keywords", "summary"]

stds_by_index = {index: [] for index in indicies}
length_by_index = {index: [] for index in indicies}

for q_i in queries3:

    query = {
        'size': 10,
        'query': {
            'match': {
                'text': q_i
            }
        }
    }

    for index in indicies:

        response = client.search(
            body=query,
            index=index
        )
        results = response["hits"]["hits"]
        # print("=========================================")
        # print("=========================================")
        # print("=========================================")
        # print(f"Index: {results[0]['_index']}")
        scores = []
        length = []
        for hit in results:
            # print("-------------------------------------")
            scores.append(hit['_score'])
            length.append(len(hit["_source"]["text"]))
            # source = hit["_source"]
            # print(f"Score: {hit['_score']}\n Text: {source['text']}")
        # print()
        # print(f"Std score: {np.std(np.array(scores))}")
        # print(f"Mean score: {np.mean(np.array(scores))}")
        # print(f"Median score: {np.median(np.array(scores))}")
        if len(scores) < 3:
            stds_by_index[index].append(0)
        else:
            stds_by_index[index].append(np.std(np.array(scores)))
        length_by_index[index].append(np.mean(length))

for index in indicies:
    print(f"Index: {index}")
    print(f"Mean std: {np.mean(np.array(stds_by_index[index]))}")
    print(f"Mean length: {np.mean(np.array(length_by_index[index]))}")
