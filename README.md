# Dataspace Workflow Execution Engine

The *Dataspace Workflow Execution Engine* executes workflow graphs provided as input in JSON format.

The workflow implements the KIT (Keep-It-Together) concept by composing interoperable assets from dataspaces into a single executable pipeline. 

The asset providers or system designers create workflows to ensure that the associated dataspace assets are accessed and executed in the predefined sequence.

In contrast, consumer users can simply execute the workflow to utilise the dataspace assets within their application as intended by the asset providers. This enables automated and repeatable pipeline execution.

The overarching concept and the workflow graph specification are found in:
- [docs/concept_overview.md](./docs/concept_overview.md)
- [docs/graph_specification.md](./docs/graph_specification.md)

## System Overview

This repository contains the execution backend engine, along with an optional GUI tool for designing and visualising workflow graphs.

The following figure illustrates how the backend execution engine and the frontend GUI can be setup and used in your system.

<img src="./docs/resources/architecture.png" alt="Architecture" width="100%">

* User A is the end user operating the robotic system.
* The local system hosts both the frontend and the backend execution engine (GUI is optional).
* The human user can create/import workflow graphs and trigger the execution through the frontend GUI.
* The backend engine can communicate with the local system via the REST API.
* The backend engine sends and receives data from the User A's dataspace connector via the Dataspace APIs.
* The backend engine can communicate with runtime environments (e.g., Kubernetes) to deploy container images received from the datsapce.

## Setup

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

### Graph Editor GUI (Optional)

Generally, the workflow can be created manually in JSON format, and sent to the backend engine via Rest API for execution.

However, using the provided GUI allows human users to visually design the graph and execute with a single button click.

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

Then run the execution engine (you need the .venv activated)

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

### Development: Code Quality (Optional)

Run `ruff` for formatting and linting via

```bash
ruff format
ruff check
```

Run `mypy` for type checking via

## Getting Started

### Step 1. Be able to create assets and contracts in the dataspace
- [DLR dataspace manual - Making Assets and Contracts](./docs/asset_creation_dlr_dataspace.pdf)
- T-System dataspace manual (To be provided later)
- What metadata should be provided when creating an asset?

### Step 2. Design a workflow


### Step 3. Distribute your workflow 

### Step 4. Execute 



## Running Examples

We recommend to check the above documentations before going through the running examples at the end of this file.

> [!NOTE]
> By default, the automatic negotiation option is disabled. For the running examples, enable it.
> However, normally you don't want to negotiate all the assets automatically. So, disabling it is generally desired.
> In this case, you can use the dataspace web portal to browse the assets and manually negotiate.

Enable auto-nego by:
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

### Optional: Backend Engine Endpoints References

```
http://localhost:8080/docs
```