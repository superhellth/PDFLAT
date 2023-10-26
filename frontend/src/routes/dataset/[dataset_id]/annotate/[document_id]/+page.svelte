<script lang="ts">
  import RegionOverlay from "./../../../../../components/RegionOverlay.svelte";
  export let data;
  import { LABELS } from "../../../../../stores/LABELS.js";
  import { onMount } from "svelte";
  import Region from "$lib/region";

  let currentPage: any = null;
  let currentIndex: number = 0;
  let allPageNumbers: number[] = [];
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
    console.log(data);
    for (var page of data.document.pages) {
      allPageNumbers.push(page.page_nr);
    }
    setLabels();
    await loadPage(currentIndex);
  });

  function setLabels() {
    LABELS.set(data.dataset.labels);
  }

  async function loadPage(index: number) {
    currentPage = data.document.pages[index];
    await loadRegions(currentPage.page_nr);
  }

  async function deletePage(pageNr: number) {
    data.document.pages = data.document.pages.filter(
      (p) => p.page_nr != pageNr
    );
    allPageNumbers = allPageNumbers.filter((p) => p != pageNr);
    if (currentIndex + 1 == allPageNumbers.length) {
      currentIndex -= 1;
    }
    const requestBody = JSON.stringify({
      document_id: data.document.document.document_id,
      page_nr: pageNr,
    });

    const res = await fetch(`http://localhost:1337/delete_page`, {
      method: "POST",
      body: requestBody,
      headers: {
        "Content-Type": "application/json",
      },
    });
    console.log(await res.json());
    await loadPage(currentIndex);
  }

  async function loadRegions(pageNr: any) {
    let response = await fetch(
      `http://127.0.0.1:1337/pages/?document_id=${data.document.document.document_id}&page_nr=${pageNr}`
    );
    let json = await response.json();
    if (json["success"] == true) {
      let labels: any[] = data.dataset.labels;
      let labelsMap = new Map<number, string>();
      for (var label of labels) {
        labelsMap.set(label.id, label.color);
      }
      lines = json["lines"].map(
        (obj) => new Region("line", obj, labelsMap.get(obj.label))
      );
      chars = json["chars"].map(
        (obj) => new Region("char", obj, labelsMap.get(obj.label))
      );
      if (activeType == "line") {
        regions = lines;
      } else {
        regions = chars;
      }
      console.log("Page reload");
      for (var region of regions) {
        if (region.getLabel() != -1) {
          console.log(region);
        }
      }
    } else {
      lines = [];
      chars = [];
      regions = [];
    }
    selectedRegions = [];
  }

  async function selectRegion(number: any) {
    console.log("Select");
    if (selectedRegions.indexOf(number) !== -1) {
      selectedRegions = selectedRegions.filter((r) => r !== number);
      return;
    }
    if (selectedRegions.length > 0) {
      let newRegion = await mergeRegions(number);
      newRegion = new Region(activeType, newRegion, "grey");
      selectedRegions = [newRegion.getNumber()];
    } else {
      selectedRegions = [...selectedRegions, number];
    }
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
  <h2>
    {data.document.document.title} Number of pages: {data.document.pages.length}
  </h2>

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
        {#key regions}
          {#each regions as region}
            <RegionOverlay
              {region}
              {deleteRegion}
              {selectRegion}
              {mergeRegions}
              selected={selectedRegions.includes(region.getNumber())}
            />
          {/each}
        {/key}
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
          {#if currentIndex > 0}
            <button
              class="px-4 py-2 bg-blue-200 border-2 cursor-pointer border-blue-300 rounded-md"
              on:click={() => {
                currentIndex -= 1;
                loadPage(currentIndex);
              }}>Previous Page</button
            >
          {/if}
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
          {#if currentIndex + 1 < allPageNumbers.length}
            <button
              class="px-4 py-2 bg-blue-200 border-2 cursor-pointer border-blue-300 rounded-md"
              on:click={() => {
                currentIndex += 1;
                loadPage(currentIndex);
              }}>Next Page</button
            >
          {/if}
          <input
            type="text"
            id="page-scroller"
            on:keyup={() => {
              let currentText = document.getElementById("page-scroller").value;
              if (currentText < allPageNumbers.length - 1 && currentText >= 0) {
                currentIndex = currentText;
                loadPage(currentIndex);
              }
            }}
          />
          <button
            class="px-4 py-2 flex bg-red-200 border-2 cursor-pointer border-red-300 rounded-md"
            on:click={() => {
              deletePage(currentPage.page_nr);
            }}>Delete Page</button
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
