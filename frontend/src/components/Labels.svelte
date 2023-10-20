<script>
  import { LABELS } from "../stores/LABELS.js";
  import Label from "./Label.svelte";
  export let setColor;
  export let region;
  export let deleteRegion;
  export let mergeRegions;
  const cols = Math.ceil(Object.keys($LABELS).length / 2);
  // grid-cols-1 grid-cols-2 grid-cols-3 grid-cols-4 grid-cols-5 grid-cols-6 grid-cols-7 grid-cols-8 grid-cols-9
  // col-span-1 col-span-2 col-span-3 col-span-4 col-span-5 col-span-6 col-span-7 col-span-8 col-span-9
</script>

<div
  on:click|stopPropagation
  on:keydown={() => {}}
  class="bg-white absolute z-50 -top-40 mt-2 w-[500px] p-4 grid grid-cols-{cols} rounded-md -left-4 border-2 border-gray-100 shadow-xl gap-2"
>
  <div
    class="col-span-{cols} grid grid-cols-{Math.max(
      2,
      cols
    )} gap-x-2 text-white"
  >
    <button
      class="bg-red-400 flex items-center rounded-md px-2 py-1"
      on:click={() => deleteRegion(region.line_nr)}
    >
      delete
    </button>
    <button
      class="bg-blue-400 flex items-center rounded-md px-2 py-1"
      on:click={() => mergeRegions(region.line_nr)}
    >
      merge
    </button>
  </div>
  {#each $LABELS as label (label.id)}
    <Label name={label.name} id={label.id} color={label.color} {region} {setColor} />
  {/each}
</div>
