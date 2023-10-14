<script>
    export let dataset;
    let newLabelName = "";
    async function createLabel() {
        const requestBody = JSON.stringify({
            dataset_id: dataset.dataset_id,
            name: newLabelName,
        });
        const result = await fetch(`http://localhost:1337/create_label_for_dataset`, {
            method: "POST",
            body: requestBody,
            headers: {
                "Content-Type": "application/json",
            },
        });
        const jsonData = await result.json();
        console.log(jsonData);
        newLabelName = "";
        dataset.labels = [...dataset.labels, jsonData.label];
    }

    async function deleteLabel(label){
        if (label.id == -1){
            return;
        }
        const requestBody = JSON.stringify({
            dataset_id: dataset.dataset_id,
            label: label
        });
        const result = await fetch(`http://localhost:1337/delete_label_for_dataset`, {
            method: "POST",
            body: requestBody,
            headers: {
                "Content-Type": "application/json",
            },
        });
        const jsonData = await result.json();
        console.log(jsonData);
        dataset.labels = dataset.labels.filter(l => l.id !== label.id);
    }

</script>

<div class="px-4 py-2 hover:bg-gray-100 rounded-md transition-all duration-200">
    <a
        rel="external"
        class="text-lg font-bold px-2"
        href="/dataset/{dataset.dataset_id}">{dataset.name}</a
    >
    <div class="flex flex-wrap">
        {#each dataset.labels as label (label.id)}
            <div
                class="text-md bg-l-4 p-2 bg-{label.color}-100 border-{label.color}-200 border-2 rounded-md m-1 cursor-pointer"
                on:click={() => deleteLabel(label)}
                on:keydown={() => {}}

            >
                {label.name}
            </div>
        {/each}
        <!-- form to create a new label -->
        <div class="flex items-center">
            <input
                class="border-2 border-gray-300 rounded-md p-2 outline-none mr-4"
                type="text"
                placeholder="New label"
                bind:value={newLabelName}
            />
            <button
                class="border-gray-300 border-2 rounded-md p-2"
                on:click={createLabel}
            >
                Create
            </button>
        </div>
    </div>
</div>
