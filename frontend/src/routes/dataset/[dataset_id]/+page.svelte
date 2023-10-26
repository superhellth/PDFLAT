<script lang="ts">
  import { onMount } from "svelte";

  export let data;
  let file: any;
  let documents_ready: boolean = false;
  let documents: Array<any>;
  let latest_response: any = {"success": false, "message": "Nothing uploaded yet"};


  onMount(async () => {
    updateDocList()
  });

  async function updateDocList() {
    let response = await fetch(
      `http://127.0.0.1:1337/get_documents_of_dataset/${data.dataset.dataset_id}`
    );
    documents = await response.json();
    console.log(documents)
    documents = Array.from(documents["documents"]);
    console.log(documents)
    documents_ready = true;
  }

  async function deleteDocument(documentID: any) {
    const requestBody = JSON.stringify({
      document_id: documentID,
    });
    // send request to API
    const result = await fetch(`http://localhost:1337/delete_document`, {
      method: "POST",
      body: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
    });
    const jsonData = await result.json();
    updateDocList()
  }

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append("file_obj", file);

    const response = await fetch(
      `http://localhost:1337/upload_pdf/${data.dataset.dataset_id}`,
      {
        method: "POST",
        body: formData,
      }
    );

    const jsonData = await response.json();
    latest_response = jsonData;
    updateDocList()
  };
</script>

<h1>Dataset Menu: {data.dataset.name}</h1>

<div>
  <h2>Upload PDF</h2>
  <label for="fileInput">Select a PDF file:</label>
  <input
    type="file"
    id="fileInput"
    on:change={(event) => {
      file = event.target.files[0];
    }}
  />

  <button class="px-4 py-2 bg-blue-200 border-2 cursor-pointer border-blue-300 rounded-md" on:click={uploadFile}>Upload</button>
  {#if latest_response["success"] == false}
    <p>{latest_response["message"]}</p>
  {:else}
    <p>Uploaded document with ID: {latest_response["document_id"]}</p>
  {/if}
</div>

<div>
  <h2>Current Documents in Dataset:</h2>
  {#if documents_ready}
    {#if documents.length > 0}
      <div>
        <ul>
          {#each documents as document}
            <li>
              <h3>{document.title}</h3>
              <h5>ID: {document.document_id}</h5>
              <button class="px-4 py-2 bg-red-200 border-2 cursor-pointer border-red-300 rounded-md" on:click={() => deleteDocument(document.document_id)} >
                Delete
              </button>
              <a
                rel="external"
                href="/dataset/{data.dataset.dataset_id}/annotate/{document.document_id}"
                >Annotate file</a
              >
            </li>
          {/each}
        </ul>
      </div>
    {:else}
      <h3>No documents uploaded</h3>
    {/if}
  {/if}
</div>
