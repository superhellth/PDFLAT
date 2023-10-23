<script lang="ts">
  import type Region from "$lib/region.js";
  import { getLabelColorByID } from "../lib/labels.js";
  import Labels from "./Labels.svelte";
  export let region: Region;
  export let correct = false;
  export let classified = false;
  export let deleteRegion: (a: Region) => void;
  export let selectRegion: (a: number) => void;
  export let mergeRegions: (a: number) => any;
  export let selected: boolean;

  /*
  bg-green-300 bg-red-300
  border-2 border-4 border-6
  */
  let color = getLabelColorByID(region.getLabel());
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
  console.log(region.getType())
  let isLine: boolean = region.getType() == "line";
</script>

<div
  on:mouseenter={() => (hover = true)}
  on:mouseleave={() => (hover = false)}
  on:click={() => {
    selectRegion(region.getNumber());
  }}
  on:keydown={() => {}}
  class="absolute bg-{color}-200 border-{color}-400 bg-opacity-{isLine ? '50': '30'} border-{selected
    ? region.getType() == "line" ? '4' : '2'
    : region.getType() == "line" ? '2' : '1'} {labelled
    ? 'z-[15]'
    : 'z-20'} hover:z-30 rounded-md outline-0 outline-[rgba(255,255,255,0)] hover:outline-[9999px] transition-all duration-300 hover:outline hover:outline-[rgba(255,255,255,0.8)]"
  style="
top: {region.getY()}px;
left: {region.getX() - 3}px;
width: {region.getWidth() + 9}px;
height: {region.getHeight() + 4}px;
"
>
  {#if hover}
    <Labels {region} {setColor} {deleteRegion} {mergeRegions} />
    <p style="margin-top: 50px" >{region.getText()}</p>
  {/if}
  {#if classified}
    {@const classifiedColor = correct ? "green" : "red"}
    <div
      class="absolute top-[50%] translate-y-[-50%] -right-8 w-4 h-4 rounded-full my-auto bg-{classifiedColor}-300"
    />
  {/if}
</div>
