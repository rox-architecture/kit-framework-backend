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
    - type `ds_static_file`: access data from the dataspace
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


## Execution Result

In the project root, download folder is created. 
There, two wine datasets and one zip file is located.
