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

```bash
mypy
```
