# canvas-execution-engine

Execution engine for the canvas.

## Setup (Development)

Install either with `pip` or `uv`

```bash
pip install -e .[dev]
```

```bash
uv sync --all-extras
```

## Run

First run

```bash
docker compose up --build
```

Then run the following in another terminal

```bash
python main.py
```

## Code Quality

Run `ruff` for formatting and linting via

```bash
ruff format
ruff check
```

Run `mypy` for type checking via


## Example Walk Through

Before we start, setup the graph editor GUI [here](https://gitlab.dlr.de/ki-dataspace/canvas-execution-engine/-/blob/main/react-flow/README.md?ref_type=heads)

### 1. Prepare .env file

```bash
cp .env.example .env
```

In the `.env` file, complete two variables, which are needed to access the dataspace API.
```
BASE_URL_DLR_CONNECTOR=...
API_KEY_DLR_CONNECTOR=...
```
- BASE_URL_DLR_CONNECTOR looks like `https://vision-x-api.base-x-ecosystem.org/connectors/jin-conn`
- API_KEY_DLR_CONNECTOR looks like `sk-...`

Our engine needs to run again to load the environment variables.
```bash
python main.py
```

### 2. Check the example workflow graph

We will use `test/ex3.json` ([here](https://gitlab.dlr.de/ki-dataspace/canvas-execution-engine/-/blob/main/test/ex3.json?ref_type=heads)) as an example.

To see the graph visually, use the "import (JSON)" feature of the GUI. Just copy+paste the graph JSON into GUI.

There are two nodes `Wine Quality Dataset for Red Wine` and `Wine Quality Dataset for White Wine`, which access the data asset in the dataspace. The parameters are briefly:
- **type**: the node type (which defines the behaviour)
- **adapter_type**: the adapter to communicate with which dataspace connector. Currently only DLR dataspace, but any dataspace connector can be added as a plugin.
- **provider_url**: connector url
- **provider_bpn**: Business Partner Number
- **asset_id**: the asset to be accessed

`Save To File` nodes then save these data into files in the local memory. Its parameter includes:
- **type**: the node type (which defines the behaviour)
- **file_path**: the path to save the data

The node parameters are defined via their `ParamSpec` schema. For instance:
- data_file ([ParamSpec](https://gitlab.dlr.de/ki-dataspace/canvas-execution-engine/-/blob/main/src/cee/node_plugins/nodes/data_file.py?ref_type=heads))
- save_to_file ([ParamSpec](https://gitlab.dlr.de/ki-dataspace/canvas-execution-engine/-/blob/main/src/cee/node_plugins/nodes/save_to_file.py?ref_type=heads))

### 3. Add the workflow into the engine

Open another terminal, and navigate to the `test` directory.

We use a provided script to trigger `http://localhost:8080/workflows`.
```
python inject_workflow.py ex3.json
```
Here, you can use any file instead of ex3.json.

This will add a workflow into the engine's database. To check, access [http://localhost:8080/workflows/show/all](http://localhost:8080/workflows/show/all).

Copy the workflow id and execute:
```
python trigger_execution.py <workflow-id>
```
Substitute your workflow id in the command. This will trigger the execution of the workflow.

After the execution, you will there is `download` folder created, and two data assets are saved as files (as specified as their respective `file_path` parameter).

> [!WARNING]
> The execution may fail in the first few runs due to the delay in the negotiation. In this case, wait a few mins for the negotiation to finish. Then, attempt again.

### 4. (Optional) Check the database 

You can observe the DB tables using software like [DBeaver](https://dbeaver.io/). 

# Tips

```mermaid

```




