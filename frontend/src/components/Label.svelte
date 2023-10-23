<script lang="ts">
  import Region from "$lib/region";

  export let name;
  export let id: number;
  export let color;
  export let region: Region;
  export let setColor;

  async function setLabel() {
    const requestBody = JSON.stringify({
      document_id: region.getDocumentID(),
      page_nr: region.getPageNR(),
      number: region.getNumber(),
      type: region.getType(),
      label_id: id,
    });
    // send request to API
    const res = await fetch(
      `http://localhost:1337/label_region`,
      {
        method: "POST",
        body: requestBody,
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
    const jsonData = await res.json();
    console.log(jsonData);
    

    setColor(color);
  }
</script>

<div
  class="py-1 px-2 leading-6 cursor-pointer hover:scale-110 rounded-md transtion-all duration-100 bg-{color}-200 border-2 border-{color}-400"
  on:click={setLabel}
  on:keydown={() => {}}
>
  {name}
</div>
