<script>
  export let name;
  export let id;
  export let color;
  export let region;
  export let setColor;

  async function setLabel() {
    console.log(region.region_id)
    console.log(id)
    const requestBody = JSON.stringify({
      region_id: region.region_id,
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
