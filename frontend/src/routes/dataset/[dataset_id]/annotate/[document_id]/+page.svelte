<script lang="ts">
  import RegionOverlay from "./../../../../../components/RegionOverlay.svelte";
  export let data;
  import { LABELS } from "../../../../../stores/LABELS.js";
  import { onMount } from "svelte";
  import Region from "$lib/region";

  let currentPage: any = null;
  let activeType: string = "line";
  let lines: any = null;
  let chars: any = null;
  let regions: Region[] = [];
  let selectedRegions: any = [];

  let mousePos = { x: 0, y: 0 };
  let markerStart = { x: 0, y: 0 };
  let markerEnd = { x: 0, y: 0 };
  let marking = false;

  onMount(async () => {
    console.log(data.document);
    setLabels();
    loadPage(0);
  });

  function setLabels() {
    LABELS.set(data.dataset.labels);
    console.log($LABELS);
  }

  async function loadPage(pageNr: any) {
    currentPage = data.document.pages[pageNr];
    loadRegions(pageNr);
  }

  async function loadRegions(pageNr: any) {
    let response = await fetch(
      `http://127.0.0.1:1337/pages/?document_id=${data.document.document.document_id}&page_nr=${pageNr}`
    );
    let json = await response.json();
    // regions = [];
    if (json["success"] == true) {
      lines = json["lines"].map((obj) => new Region("line", obj));
      chars = json["chars"].map((obj) => new Region("char", obj));
      if (activeType == "line") {
        regions = lines;
      } else {
        regions = chars;
      }
    } else {
      lines = [];
      chars = [];
      regions = [];
    }
    console.log("Loaded page");
    for (var region of regions) {
      if (region.getLabel() != -1) {
        console.log(region);
      }
    }
    selectedRegions = [];
  }

  async function selectRegion(number: any) {
    console.log("Select");
    if (selectedRegions.indexOf(number) !== -1) {
      selectedRegions = selectedRegions.filter((r) => r !== number);
      console.log(selectedRegions);
      return;
    }
    if (selectedRegions.length > 0) {
      let newRegion = await mergeRegions(number);
      newRegion = new Region(activeType, newRegion);
      selectedRegions = [newRegion.getNumber()];
    } else {
      selectedRegions = [...selectedRegions, number];
    }
    console.log(selectedRegions);
  }

  async function mergeRegions(line_nr: any) {
    console.log("merge regions");
    // add region_id to selected regions if its not in there yet
    if (selectedRegions.indexOf(line_nr) === -1) {
      selectedRegions = [...selectedRegions, line_nr];
    }
    console.log(selectedRegions);
    // call merge regions api endpoint
    const requestBody = JSON.stringify({
      region_ids: selectedRegions,
      document_id: data.document.document.document_id,
      page_nr: currentPage["page_nr"],
    });
    let response = await fetch(`http://localhost:1337/merge_lines`, {
      method: "POST",
      body: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
    });
    let jsonData = await response.json();

    // remove all deleted from regions
    regions = regions.filter(
      (r) => !jsonData["delete_line_nrs"].includes(r.getNumber())
    );
    selectedRegions = [];

    // add new region to regions
    regions = [...regions, new Region(activeType, jsonData.region)];

    // remove all regions from selected regions
    selectedRegions = [];
    return jsonData.region;
  }

  async function deleteRegion(region: Region) {
    await fetch(
      `http://localhost:1337/${region.getType()}?document_id=${
        data.document.document.document_id
      }&page_nr=${
        currentPage["page_nr"]
      }&${region.getType()}_nr=${region.getNumber()}`,
      {
        method: "DELETE",
      }
    );
    regions = regions.filter((r) => r.getNumber() !== region.getNumber());
    selectedRegions = selectedRegions.filter((r) => r !== region.getNumber());
  }
</script>

<body>
  <h1>Annotating</h1>
  <h2>{data.document.document.title}</h2>

  <div
    class="w-screen h-screen overflow-scroll flex items-left justify-start flex-col p-4"
  >
    {#if currentPage != null}
      <div
        style="width: {currentPage.page_width +
          4}px; height: {currentPage.page_height + 4}px;"
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
          class="border-gray-500 border-2 rounded-md relative w-[{currentPage.page_width}px]"
          src="http://localhost:1337{currentPage.image_path}"
          alt="pdf page"
        />
        {#each regions as region}
          <RegionOverlay
            {region}
            {deleteRegion}
            {selectRegion}
            {mergeRegions}
            selected={selectedRegions.includes(region.getNumber())}
          />
        {/each}
        <div
          class="w-full h-full absolute top-0 left-0 {marking
            ? 'z-50'
            : 'z-10'}"
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
            // createRegion();
          }}
        />
        <div
          class="bg-gray-300 bg-opacity-30 border-gray-200 border-2 rounded-md absolute z-50 pointer-events-none"
          style="top:{markerStart?.y}px; left:{markerStart?.x}px; width:{markerEnd?.x -
            markerStart?.x}px; height:{markerEnd?.y - markerStart?.y}px;"
        />
        <div class="flex w-full items-center justify-center my-4 gap-4">
          <button
            class="px-4 py-2 flex bg-red-200 border-2 cursor-pointer border-red-300 rounded-md"
            on:click={() => {
              if (activeType == "char") {
                activeType = "line";
              } else {
                activeType = "char";
              }
              loadRegions(currentPage.page_nr);
            }}>Toggle Type</button
          >
          <button
            class="px-4 py-2 bg-blue-200 border-2 cursor-pointer border-blue-300 rounded-md"
            on:click={() => {
              currentPage = data.document.pages[currentPage["page_nr"] + 1];
              loadRegions(currentPage["page_nr"]);
            }}>Next Page</button
          >
        </div>
      </div>
    {/if}
  </div>
</body>

<style>
  body {
    background-color: lightcyan;
  }
</style>
