# Running Example 2

We will execute `running_example2.json` in the test directory.

In this example, we build a container image from the dataspace asset.

This example requires Docker installed.
```bash
docker -v
```

The workflow graph looks like this:

<img src="./resources/example_graph2.png" alt="Architecture" width="100%">

## Main observations:
- Node **Py3.12 Container** has
    - type: `ds_container` operational type
    - adapter_type `dlr_connector`: talk to the DLR dataspace connector (or `ts_connector` for T-System dataspace)
    - provider_url: the URL of the provider's connector URL
    - provider_bpn: provider's Business Partner Number (BPN)
    - asset_id: ID of the asset to access
    - representation `Dockerfile`: the asset is a Dockerfile
    - platform `linux/amd64`: target deployment platform

## Expected result:
- The python3.12 container image with name:mytestpython and tag:test will be made available in `docker images`.

## Execution Result

Check if the container image `mytestpython:test` is available
```
docker images
```

