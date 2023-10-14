<script>
  export let data;
  import { LABELS } from "../../../../stores/LABELS.js";
  import Region from "../../../../components/Region.svelte";
  import { onMount } from "svelte";
  // call backend api to retrieve a document
  // and pass it to the component

  let regions, page;

  let mousePos = { x: 0, y: 0 };
  let markerStart = { x: 0, y: 0 };
  let markerEnd = { x: 0, y: 0 };
  let marking = false;
  let selected_regions = [];

  async function loadPage() {
    const res = await fetch(
      `http://localhost:1337/get_unlabelled_page/${data.dataset.dataset_id}`
    );
    const jsonData = await res.json();
    console.log(jsonData);
    page = jsonData.page;
    regions = jsonData.regions;
    console.log(regions);
  }

  async function mergeRegions(region_id) {
    console.log("merge regions");
    // add region_id to selected regions if its not in there yet
    if (selected_regions.indexOf(region_id) === -1) {
      selected_regions = [...selected_regions, region_id];
    }
    // call merge regions api endpoint
    const requestBody = JSON.stringify({
      region_ids: selected_regions,
    });
    let response = await fetch(`http://localhost:1337/merge_regions`, {
      method: "POST",
      body: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
    });
    let jsonData = await response.json();

    // remove all deleted from regions
    regions = regions.filter(
      (r) => !jsonData["delete_region_ids"].includes(r.region_id)
    );

    // add new region to regions
    regions = [...regions, jsonData.region];

    // remove all regions from selected regions
    selected_regions = [];
    return jsonData.region;
  }

  async function deleteRegion(region_id) {
    await fetch(`http://localhost:1337/region/${region_id}`, {
      method: "DELETE",
    });
    regions = regions.filter((r) => r.region_id !== region_id);
    selected_regions = selected_regions.filter((r) => r !== region_id);
  }

  async function selectRegion(region_id) {
    if (selected_regions.indexOf(region_id) !== -1) {
      selected_regions = selected_regions.filter((r) => r !== region_id);
      return;
    }
    if (selected_regions.length > 0) {
      let newRegion = await mergeRegions(region_id);
      selected_regions = [newRegion.region_id];
    } else {
      selected_regions = [...selected_regions, region_id];
    }
  }

  async function createRegion() {
    const requestBody = JSON.stringify({
      document_id: page.document_id,
      page_nr: page.page_nr,
      x_min: markerStart.x,
      y_min: markerStart.y,
      x_max: markerEnd.x,
      y_max: markerEnd.y,
    });

    const res = await fetch(`http://localhost:1337/region`, {
      method: "POST",
      body: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
    });

    const jsonData = await res.json();
    if (jsonData.success) {
      // remove all deleted from regions
      regions = regions.filter(
        (r) => !jsonData["delete_region_ids"].includes(r.region_id)
      );
      regions = [...regions, jsonData.region];
    }
    markerStart = { x: 0, y: 0 };
    markerEnd = { x: 0, y: 0 };
    marking = false;
  }

  async function nextPage() {
    // call label page api
    const requestBody = JSON.stringify({
      document_id: page.document_id,
      page_nr: page.page_nr,
    });

    const res = await fetch(`http://localhost:1337/label_page`, {
      method: "POST",
      body: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
    });

    await loadPage();
  }

  async function deletePage(){
    // call delete page api
    const requestBody = JSON.stringify({
      document_id: page.document_id,
      page_nr: page.page_nr,
    });

    const res = await fetch(`http://localhost:1337/delete_page`, {
      method: "POST",
      body: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
    });
    await loadPage();
  }

  function setLabels() {
    LABELS.set(data.dataset.labels);
    console.log($LABELS);
  }

  onMount(async () => {
    setLabels();
    await loadPage();
  });
</script>

<svelte:head>
  <title>Home</title>
  <meta name="description" content="Annotate {data.dataset.name}" />
</svelte:head>

<a rel="external" href="/dataset/{data.dataset.dataset_id}">back to dataset</a>

<div
  class="w-screen h-screen overflow-scroll flex items-left justify-start flex-col p-4"
>
  {#if page !== undefined}
    <div
      style="width: {page.page_width + 4}px; height: {page.page_height + 4}px;"
      class="relative my-4"
      on:mousemove={(e) => {
        var rect = e.target.getBoundingClientRect();
        mousePos = {
          x: e.clientX - rect.left,
          y: e.clientY - rect.top,
        };
      }}
    >
      <img
        class="border-gray-500 border-2 rounded-md relative w-[{page.page_width}px]"
        src="http://localhost:1337{page.image_path}"
        alt="pdf page"
      />
      {#each regions as region (region.region_id + region.label)}
        <Region
          {region}
          {deleteRegion}
          {selectRegion}
          {mergeRegions}
          selected={selected_regions.includes(region.region_id)}
        />
      {/each}
      <div
        class="w-full h-full absolute top-0 left-0 {marking ? 'z-50' : 'z-10'}"
        on:mousedown={() => {
          marking = true;
          markerStart = mousePos;
          markerEnd = mousePos;
        }}
        on:mousemove={() => {
          if (!marking) return;
          markerEnd = mousePos;
        }}
        on:mouseup={() => {
          marking = false;
          createRegion();
        }}
      />
      <div
        class="bg-gray-300 bg-opacity-30 border-gray-200 border-2 rounded-md absolute z-50 pointer-events-none"
        style="top:{markerStart?.y}px; left:{markerStart?.x}px; width:{markerEnd?.x -
          markerStart?.x}px; height:{markerEnd?.y - markerStart?.y}px;"
      />
      <div class="flex w-full items-center justify-center my-4 gap-4">
        <button class="px-4 py-2 flex bg-red-200 border-2 cursor-pointer border-red-300 rounded-md" on:click={deletePage}
          >delete page</button
        >
        <button class="px-4 py-2 bg-blue-200 border-2 cursor-pointer border-blue-300 rounded-md" on:click={nextPage}
          >next page</button
        >
      </div>
    </div>
  {/if}
</div>
