# Dataspace Asset Composition Framework

The Dataspace Asset Composition Framework enables users to compose and execute workflows using existing dataspace assets. While the framework facilitates the rapid utilization of these assets, the resulting data can be published back to the dataspace as new assets, continuously enriching the digital ecosystem.
This framework follows the KIT (Keep-It-Together) concept, enabling assets in the digital ecosystem to interact with each other.

A workflow is represented as a directed acyclic graph (DAG), where nodes represent functional units and edges capture execution order and data dependencies.
- The summary of the overall concept and framework architecture can be found in [docs/concept_overview.md](./docs/concept_overview.md)
- The explanation of the workflow graph can be found in [docs/graph_specification.md](./docs/graph_specification.md)

We recommend to check the above documentations before going through the running examples at the end of this file.

## Setup (Development)

Install either with `pip` or `uv`. 

```bash
uv sync --all-extras
```

```bash
pip install -e .[dev]
```

Next, prepare the `.env` file.

```bash
cp .env.example .env
```

Open the `.env` file and provide necessary information to access either DLR or T-System dataspaces.
```
BASE_URL_DLR_CONNECTOR=...
API_KEY_DLR_CONNECTOR=...
```

### Optional: Graph Editor GUI

While users can create the workflow graph in JSON manually and pass it to the execution engine via Rest API, we provide GUI to make your life easier.
With the GUI, you can:
- Graphically create and edit graphs
- Import/Export graphs
- Play button to execute the graph (auto interaction with the execution engine)

To install, go to the react-flow directory:
```
cd react-flow
```

Then, install a React-Flow server. Note that you need `npm` with version >10.
```
npm create vite@latest react-flow-editor -- --template react
cd react-flow-editor
npm install
npm install @xyflow/react
```

Then, copy the `react-App.jsx` file
```
cp ../App.jsx src/App.jsx
```

Check if everything is installed correctly
```
npm list @xyflow/react
```

If (empty) is shown, then try again:
```
npm install @xyflow/react
```

## Run

First run the database needed for the executione engine.

```bash
docker compose up --build -d
```

Then run the execution engine

```bash
python main.py
```

Alternatively using `uv`, 

```bash
uv run python main.py
```

In another terminal, run the GUI:
```
cd react-flow/react-flow-editor
npm run dev
```

### Optional: Backend Engine Endpoints References

```
http://localhost:8080/docs
```

### Optional: Code Quality (Development)

Run `ruff` for formatting and linting via

```bash
ruff format
ruff check
```

Run `mypy` for type checking via

## Running Examples

> [!NOTE]
> By default, the automatic negotiation option is disabled. 
> For the running examples, enable it by running the below command: 

```bash
cd test
python activate_auto_nego.py
```

- [Running Example 1 - dataspace asset local save and management ](./docs/running_example1.md)
- [Running Example 2 - dataspace asset container image build](./docs/running_example2.md)
- [Running Example 3 - dataspace asset container image build and kubernetes deployment](./docs/running_example3.md)
- [Asset creation - how to create assets and contracts](./docs/asset_creation_dlr_dataspace.pdf)

## Additional Documentations:
- [Execution Mode Configurations](./docs/execution_modes.md)

