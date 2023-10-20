export async function load({ fetch, params }) {
    let response = await fetch(`http://127.0.0.1:1337/datasets/${params.dataset_id}`);
    let json = await response.json();

    response = await fetch(`http://127.0.0.1:1337/documents/${params.document_id}`);
    let json2 = await response.json();
    return { dataset: json.dataset, document: json2 };
}