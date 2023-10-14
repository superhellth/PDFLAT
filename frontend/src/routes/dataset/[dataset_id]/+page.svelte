<script>
  export let data;
  let file;

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append("file_obj", file);

    console.log(formData);

    const response = await fetch(`http://localhost:1337/upload_pdf/${data.dataset.dataset_id}`, {
      method: "POST",
      body: formData,
    });

    const jsonData = await response.json();
    console.log(jsonData); // Handle the response as per your requirements
  };
</script>

{data.dataset.dataset_id}

<div data-sveltekit-preload-data="off">
  <a rel="external" href="/dataset/{data.dataset.dataset_id}/annotate">annotate</a>
</div>

<h1>Upload PDF</h1>

<label for="fileInput">Select a PDF file:</label>
<input
  type="file"
  id="fileInput"
  on:change={(event) => {
    file = event.target.files[0];
  }}
/>

<button on:click={uploadFile}>Upload</button>
