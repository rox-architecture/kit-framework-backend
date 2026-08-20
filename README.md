# KIT framework backend

## Run

First run the database needed for the executione engine.

```bash
docker compose up --build -d
```

For those with Kubernetes environment, you can also enable the kubernetes deployment.
```bash
export KUBECONFIG_HOST_PATH="$HOME/.kube/config"

docker compose \
  -f docker-compose.yml \
  -f docker-compose.kubernetes.yml \
  up -d
```

Then run the execution engine (you need the .venv activated)

Node inputs and outputs are exchanged through the `execution_artifacts` Docker
volume rather than Redis, so large binary values do not enter the task broker.
The worker mounts `/var/run/docker.sock` for Docker-backed node types. Remove
that mount if those nodes are not used; access to the Docker socket grants the
worker host-level Docker privileges.

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

## Funding

This open-source project was developed within the *[ROX](https://www.project-rox.ai/en/)* project. 
This project has received public funding from the **European Union** NextGenerationEU within the Important Project of Common European Interest – Cloud Infrastructures and Services (IPCEI-CIS) under grant agreement 13IPC034.

<p align="center">
  <img alt="Bundesministerium für Wirtschaft und Energie (BMWE)-EU and secunet funding logo" src="https://github.com/rox-architecture/kit-framework-backend/blob/main/bmwe_logo.png" width="400"/>
</p>
