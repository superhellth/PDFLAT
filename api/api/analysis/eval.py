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

keywords = ['Article', 'European', 'Member', 'States', 'State', 'Union', 'European Union', 'COUNCIL', 'EUROPEAN PARLIAMENT', 'REGULATION', 'Commission',
'group', 'electricity sector', 'coordination', 'internal market', 'COMMISSION DECISION', 'Volume', 'Member States', 'COUNCIL DECISION',
'European Economic', 'European Parliament', 'Cooperation of Energy', 'Community', 'Finnish special edition', 'Member States adopt', 'electricity', 'Climate Change', 'languages', 'official languages', 'Community Official Journal', 'DIRECTIVE', 'Nations Framework', 'special edition Chapter', 'market', 'Chapter', 'EEC Council', 'Economic Community', 'Economic Community Official', 'Union Agency', 'transmission', 'system', 'Avis juridique', 'internal electricity market', 'Treaty on European', 'United Nations', 'special edition', 'European Environment Agency', 'June', 'distribution system operators', 'Member State concerned', 'Agreement adopted', 'requires Member States', 'Council Directive', 'Annex', 'Union territorial typologies', 'European Community', 'Avis juridique important', 'Paris Agreement adopted', 
'PARLIAMENT', 'Council Regulation', 'Regulation', 'European Council', 'Council', 'critical benchmark', 'European Commission', 'European Communities',
'individual Member States', 'LAU', 'transmission system', 'delegated', 'Paris-aligned', 'Member State', 'Centre budget', 'electricity supply', 'act', 'Management Board consisting', 'European Union Official', 'Official Journal', 'gas supplies', 'Translation', 'Paris Agreement replaces', 'Economic and Social', 'residence', 'European Statistical System', 'Commission expert groups', 'EESC', 'Member State requesting', 'information', 'Energy Regulators', 'supply', 'acts', 'Social Committee', 'Schengen', 'office or agency', 'Regulations', 'Member State wishing', 'gas', 'Member State entitle', 'Commission Regulation', 'Member State fulfils', 'Member State taking', 'Member States concerned', 'entities', 'Paris Agreement requires', 'Swiss Confederation association', 'Council Decision', 'European Energy', "Member States' experts", 'investigations', 'network', 'NUTS', 'Centre revenue', 'Staff', 'Transition', 'Member State represents', 'Agreement', 'State participation', 'residence permit', 'Institutions agree', 'Member State competent', 'system operators', 'Nations Framework Convention', 'checks', 'energy policy', "Communities' financial interests", 'neighbouring Member States', 'capacity', 'inspections', 'Union legislation', 'systems', 'Member State authorities', 'gas supply policy', 'infrastructure protection', 'products', 'United Nations Framework', 'bodies and offices', 'European Economic Community', 'Decision', 'accordance with Article', "European Communities'", 'COMMISSION', 'ECIs', 'Member State referred', 'European Union decisions', 'Climate', 'prevent Member States', 'GEOGRAPHICAL INDICATIONS Article', 'Parliament', 'Board', 'Text with EEA', 'NUTS classification', 'electricity coordination', 'States concerned', 'Member State concerned.Article', 'Paris Agreement', 'coordination group', 'Paris', 'greenhouse gas', 'energy infrastructure', 'Member States recognize', 'European Communitiesconcerning internal', 'plan', 'Community reduction commitment', 'geographical', 'Projects of common', 'Union list', 'Implementation Member States', 'European electricity system', 'Convention on Climate', 'enable Member States', 'European Energy Union', 'European critical', 'gas emissions', 'WATSON Consultation', 'potential ECI', 'Graham WATSON', 'Member State set', 'Energy Union', 'Directive', 'significant environmental effects', 'Agency', 'offices and agencies', 'distribution system operator', 'subparagraph of Article', 'Schengen acquis', 'Sixth Community Environment', 'checks and inspections', 'System Operators', 'register', 'product', 'protected geographical', 'offices', 'Swiss Confederation', 'analytical method', 'European Monitoring Centre', 'Communities', 'operator', 'Member States individually', 'purpose Member States', 'European Community programme', 'Member State legislation', 'benchmark administrators', 'Pollutant Release', 'Management', 'delegated acts', 'Commission inspectors', 'natural gas transmission', 'Eleventh Council Directive', 'gas transmission', 'State concerned', 'emissions', 'gas supply', 'authorization', 'Commission Work', 'cycle greenhouse gas', 'operators', 'system operation Article', 'PRTR', 'ECI', 'energy', 'Member State level', 'EUROPEAN COMMISSION', 'Interinstitutional Agreement', 'projects', 'relevant Member States', 'respective Member State', 'Member States retain', 'interconnection of registers', 'distribution system', 'Programme', 'geographical indications', 'Member States adopted', 'pursuant to Article', 'Communities’', 'subparagraph Article', 'Consultation European Commission', 'gas emissions permit', 'storage system operators', 'allowances', 'Community emission allowance', 'populous Member State', 'Paris-aligned Benchmarks Article', 'project', 'Institutions', 'system of interconnection', 'gas transmission networks', 'Staff Regulations', "European Communities' financial", 
'system operator', 'programmes', 'transmission system operator', 'Member States registers', 'national transmission systems', 'gas emission allowance', 'Energy',
'critical infrastructure', 'issuing Member State', 'emission allowance trading', 'European Parliament elected', 'transmission system operators',
'Transmission System', 'defence service providers', 'Member State national', 'ENTSO for Gas', 'cross-zonal capacity', 'European Medicines', 'agency seats',
'agencies', 'common interest', 'European Union Agency', 'storage permit pursuant', 
'network users', 'TSOs', 'Regulation Article', 'pursuant', 'energy efficiency renovations', 'sector', 'competent authority pursuant', 'plans', 'environmental',
'Common Approach sets', 'protected geographical indications', 'European Pollutant Release', 'neighbouring TSOs', 'Security Liaison Officer', 'fuel',
'Energy Community', 'benchmark', 'Approach', 'Steel Community', 'Members', 'plan or programme', 'Atomic Energy', 'capacity calculation methodology',
'European Police Office', 'Protocol', 'energy efficiency target', 'Union energy efficiency', 'restoration service providers', 'Framework Convention',
'ACER Article', 'European Communities provided', 'resources', 'Anti-fraud Office provide', 'receiving Member State', 'host Member',
'Information Systems Security', 'Member States making', 'Member State scheme', 'EUROPEAN COUNCIL', 'Human', 'investigation', 'European PRTR information',
'greenhouse gas emissions', 'Commission premises', 'bidding zone', 'regulatory authority', 'Benchmarks', 'technical building', 'Community scheme',
'accordance', 'electricity crisis Member', 'Environmental assessment', 'critical infrastructure protection', 'European Central Bank', 'registers',
'Article transmission system', 'Common', 'Member State cooperation', 'plans and programmes', 'frequency', 'capacity calculation region',
'energy performance certificates', 'European critical infrastructure', 'Fuel Component', 'restoration', 'single day-ahead coupling', 'supplier Member States',
'national electricity crisis', 'Office', 'Member State finds', 'Commission security policy', 'gas transmission systems', 'fossil fuel',
'Hydrotreated vegetable oil', 'Administrative', 'Member State energy', 'Commission Delegated Regulation', 'Member States limit', 'STATE GREENHOUSE GAS',
'European Coal', 'Member States authorize', 'relevant Member State', 'data', 'Delegated Regulation', 'intraday coupling Article', 'storage complex',
'energy savings', 'Default greenhouse gas', 'COUNCIL DIRECTIVE']

keyword_queries_top = keywords[:10]
keyword_queries_random = [keywords[i] for i in np.random.choice(np.arange(len(keywords)), size=10, replace=False)]

# Generate 10 information retrieval example queries using keywords on the topic of energy politics in the EU with a special focus on these 5 topics:
# measures  to  safeguard  the  security  of  gas  supply,
# he  Governance  of  the  Energy  Union  and  Climate  Action, 
# risk-preparedness in the electricity sector,
# establishing a European Union Agency for the Cooperation of Energy Regulators,
# on the internal market for electricity 
chatgpt_queries = ["EU gas supply security measures 2023",
            "Energy Union and Climate Action governance in the EU",
            "Electricity sector risk-preparedness policies in the European Union",
            "Role of the European Union Agency for the Cooperation of Energy Regulators in energy politics",
            "Internal market for electricity regulations in the EU",
            "Recent developments in EU energy politics: safeguarding gas supply",
            "Challenges and strategies for ensuring electricity sector risk-preparedness in the European Union",
            "Governance framework of the Energy Union and Climate Action in the EU",
            "Impact of the European Union Agency for the Cooperation of Energy Regulators on energy market integration",
            "Assessment of internal market dynamics in the EU for electricity in 2023"]

handcrafted_queries = [
    ""
]

indicies = ["default", "insert", "bm25", "keywords", "summary"]

stds_by_index = {index: [] for index in indicies}
length_by_index = {index: [] for index in indicies}

for q_i in keyword_queries_random:

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
