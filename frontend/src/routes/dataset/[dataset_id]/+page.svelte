<script lang="ts">
  import { onMount } from "svelte";

  export let data;
  let file: any;
  let documents_ready: boolean = false;
  let documents: Array<any>;

  onMount(async () => {
    let response = await fetch(
      `http://127.0.0.1:1337/get_documents_of_dataset/${data.dataset.dataset_id}`
    );
    documents = await response.json();
    documents = Array.from(documents[0]);
    documents_ready = true;
  });

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append("file_obj", file);

    console.log(formData);

    const response = await fetch(
      `http://localhost:1337/upload_pdf/${data.dataset.dataset_id}`,
      {
        method: "POST",
        body: formData,
      }
    );

    const jsonData = await response.json();
    console.log(jsonData); // Handle the response as per your requirements
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

  <button on:click={uploadFile}>Upload</button>
</div>

<div>
  <h2>Current Documents in Dataset:</h2>
  {#if documents_ready}
    {#each documents as document}
      <div>
        <ul>
          <li>
            <h3>{document}</h3>
            <a rel="external" href="/dataset/{data.dataset.dataset_id}/annotate"
              >Annotate file</a
            >
          </li>
        </ul>
      </div>
    {/each}
  {/if}
</div>
