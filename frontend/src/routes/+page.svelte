<script>
  // import onMount from svelte
  import { apiCallFrontend } from "$lib/apiCall";
  import { onMount } from "svelte";
  import Dataset from "../components/Dataset.svelte";

  let newDatasetName = "";

  let datasets = [];
  onMount(async () => {
    let datasetsJson = await apiCallFrontend("datasets");
    datasets = datasetsJson["datasets"];
  });

  async function createDataset() {
    const requestBody = JSON.stringify({
      name: newDatasetName,
    });
    // send request to API
    const result = await fetch(`http://localhost:1337/dataset`, {
      method: "POST",
      body: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
    });
    const jsonData = await result.json();
    console.log(jsonData);
    datasets = [...datasets, jsonData.dataset];
    newDatasetName = "";
  }
</script>

<h1 class="p-4 text-2xl">Datasets</h1>

<div class="grid grid-cols-4 p-4">
  {#each datasets as dataset (dataset.dataset_id)}
    <Dataset {dataset} />
  {/each}
  <!-- form to create a new dataset -->
  <div
    class="px-4 py-2 hover:bg-gray-100 rounded-md transition-all duration-200 flex items-center justify-center"
  >
    <input
      class="border-2 border-gray-300 rounded-md p-2 outline-none mr-4"
      type="text"
      placeholder="New dataset"
      bind:value={newDatasetName}
    />
    <button
      class="border-gray-300 border-2 rounded-md p-2"
      on:click={createDataset}
    >
      Create
    </button>
  </div>
</div>