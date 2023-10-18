export let prerender = false;
export async function load({ fetch, params }) {
    let response = await fetch(`http://127.0.0.1:1337/datasets/${params.dataset_id}`);
    let json = await response.json();
    // let response = await fetch(`http://127.0.0.1:1337/get_documents_of_dataset/${params.dataset_id}`)
    return { dataset: json.dataset };
}
