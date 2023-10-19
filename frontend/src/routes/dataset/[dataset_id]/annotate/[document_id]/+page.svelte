<script lang="ts">
  export let data;
  import { LABELS } from "../../../../../stores/LABELS.js";
  import Region from "../../../../../components/Region.svelte";
  import { onMount } from "svelte";
    import { page } from "$app/stores";

  let currentPage: any = null;
  let lines: any = null;
  let chars: any = null;

  let mousePos = { x: 0, y: 0 };
  let markerStart = { x: 0, y: 0 };
  let markerEnd = { x: 0, y: 0 };
  let marking = false;

  onMount(async () => {
    console.log(data.document);
    loadPage(0)
  });

  async function loadPage(pageNr: any) {
    currentPage = data.document.pages[pageNr]
    loadRegions(pageNr)
  }

  async function loadRegions(pageNr: any) {
    let response = await fetch(`http://127.0.0.1:1337/pages/?document_id=${data.document.document.document_id}&page_nr=${pageNr}`)
    let json = await response.json();
    lines = json["lines"]
    chars = json["chars"]
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
        <!-- {#each regions as region (region.region_id + region.label)}
          <Region
            {region}
            {deleteRegion}
            {selectRegion}
            {mergeRegions}
            selected={selected_regions.includes(region.region_id)}
          />
        {/each} -->
      </div>
      <!--
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
    </div> -->
    {/if}
  </div>
</body>

<style>
  body {
    background-color: lightgray;
  }
</style>
