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




