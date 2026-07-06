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

--- 

### Test Purpose Graph Editor GUI

Go to the react-flow directory:
```bash
cd react-flow
```

Then, install a React-Flow server. You need `npm`.
```bash
npm create vite@latest react-flow-editor -- --template react
cd react-flow-editor
npm install
npm install @xyflow/react
```

Overwrite the `App.jsx` file:
```bash
mv ../App.jsx src/App.jsx
```

Check if everything is installed correctly
```bash
npm list @xyflow/react
```
If (empty) is shown, then try again:
```bash
npm install @xyflow/react
```

Now, run the GUI by:
```bash
npm run dev
```
You can access the GUI via `http://localhost:5173/` 

---

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


