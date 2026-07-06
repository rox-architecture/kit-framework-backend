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


## Getting Started With An Example

To play with our engine, the user needs an easy way to create and modify the workflow graphs, to observe the outputs of our engine. For this, we first setup a test-purpose graph editor GUI. After the GUI setup, we will go through our example step-by-step. 


### Step-by-step Example Walk Through

First, we make the `.env` file. In the console,

```bash
cp .env.example .env
```

Then, open `.env` with a text editor, and complete the two variables. These variables are needed to access the dataspace API.
```
BASE_URL_DLR_CONNECTOR=...
API_KEY_DLR_CONNECTOR=...
```
- BASE_URL_DLR_CONNECTOR looks like `https://vision-x-api.base-x-ecosystem.org/connectors/jin-conn`
- API_KEY_DLR_CONNECTOR looks like `sk-...`

Now, run the engine to load the environment variables. If it was already running, close it and run again. 
```bash
python main.py
```


