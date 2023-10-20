<script>
  import { getLabelColorByID } from "../lib/labels.js";
  import Labels from "./Labels.svelte";
  export let region;
  export let correct = false;
  export let classified = false;
  export let deleteRegion;
  export let selectRegion;
  export let mergeRegions;
  export let selected;

  /*
  bg-green-300 bg-red-300
  border-2 border-4 border-6
  */

  let color = getLabelColorByID(region.label);
  let labelled = false;
  if (!color) {
    color = "gray";
    labelled = true;
  }
  const setColor = (c) => {
    color = c;
    labelled = true;
  };
  let hover = false;
</script>

<div
  on:mouseenter={() => (hover = true)}
  on:mouseleave={() => (hover = false)}
  on:click={() => {
    selectRegion(region["line_nr"]);
  }}
  on:keydown={() => {}}
  class="absolute bg-{color}-200 border-{color}-400 bg-opacity-30 border-{selected ? "4" : "2"} {labelled
    ? 'z-[15]'
    : 'z-20'} hover:z-30 rounded-md outline-0 outline-[rgba(255,255,255,0)] hover:outline-[9999px] transition-all duration-300 hover:outline hover:outline-[rgba(255,255,255,0.8)]"
  style="
top: {region.y - 3}px;
left: {region.x - 3}px;
width: {region.width + 9}px;
height: {region.height + 6}px;
"
>
  {#if hover}
    <Labels {region} {setColor} {deleteRegion} {mergeRegions} />
  {/if}
  {#if classified}
    {@const classifiedColor = correct ? "green" : "red"}
    <div
      class="absolute top-[50%] translate-y-[-50%] -right-8 w-4 h-4 rounded-full my-auto bg-{classifiedColor}-300"
    />
  {/if}
</div>
