# Running Example 1

We will execute `running_example1.json` in the test directory.

In this example, we download some AI training datasets and zip them into one compression file.

First, observe the graph by:
- access the GUI at http://localhost:5173/ and import the graph (use the import JSON buttom)
- or directly looking into the JSON file

The graph looks like this:

<img src="./resources/example_graph1.png" alt="Architecture" width="100%">

## Main observations:
- Node **White Wine Dataset**
    - type `ds_data_file`: access data from the dataspace
    - adapter_type `dlr_connector`: talk to the DLR dataspace connector (or `ts_connector` for T-System dataspace)
    - provider_url: the URL of the provider's connector URL
    - provider_bpn: provider's Business Partner Number (BPN)
    - asset_id: ID of the asset to access
- Node **Red Wine Dataset**
    - Similar to the White Wine Dataset node but with a different asset_id
- Node **Save To File**
    - type `save_to_file`: will save the input data to a local file
    - file_path: path to save the file (the root is the backend running directory)
- Node **zipper**
    - type `zipper`: will zip all the files in the target_directory
    - output_path: the resulting zip file name and location
    - With the `dep` connections, it is triggered only after the two Save To File nodes

## Expected result:
- White and Red wine datasets are saved into local files, and zipped.

## Run the workflow:

Keep your backend engine terminal visible to observe the console outputs.

### Run Method 1

In GUI, find the green button on the right top screen, click it

### Run Method 2

Use Rest API to trigger the execution. For now, we can use `curl` at the root directory.

```bash
curl -X POST http://localhost:8080/workflows \
  -H "Content-Type: application/json" \
  --data "{\"workflow_name\":\"my-workflow\",\"graph_json\":$(cat test/running_example1.json)}"
```

In the response, find the `workflow_id` to make the next request (replace `<<workflow_id>>` with the id value)
```bash
curl -X POST http://localhost:8080/execution/request \
  -H "Content-Type: application/json" \
  --data '{"workflow_id":"<<workflow_id>>"}'
```

## Execution Result

In the project root, download folder is created. 
There, two wine datasets and one zip file is located.
