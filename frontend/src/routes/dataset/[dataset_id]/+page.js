export let prerender = false;
export async function load({ fetch, params }) {
    let response = await fetch(`http://api/datasets/${params.dataset_id}`);
    let json = await response.json();
    return { dataset: json.dataset };
}
