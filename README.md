# CMZ-chatbots
A repository for the CMZ chatbot program

## History Tracking Requirement

**All contributors must create a session history log before committing code.**

1. Create a file in the `/history/` directory named: `{your_name}_{YYYY-MM-DD}_{start_time}h-{end_time}h.md`
2. Include all prompts, MCP server usage, actions, commands, and technical details from your development session
3. Use 4-hour time windows for session tracking
4. This ensures project continuity and knowledge transfer across team members

**Example**: `history/kc.stegbauer_2025-09-07_09h-13h.md`

OpenAPI spec:
TODO:  Change this link after initial checkin
[View CMZ API in Swagger UI](https://petstore.swagger.io/?url=https://raw.githubusercontent.com/nortal/CMZ-chatbots/kcs/openapi_checkin/backend/api/openapi_spec.yaml)


# Using the API Makefile

This Makefile automates generating a Flask server from an OpenAPI spec, building a Docker image, and running a live container. It also includes optional local Python tooling with **uv**.

> For a full list of targets and variables, run:
>
> ```bash
> make help
> ```


## Prerequisites

* **Docker** (required for code generation, image build, and running the API)
* **GNU make**
* **uv** (optional; only needed for the local virtualenv utilities)

Install uv: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

## Minimal workflow: get a Flask API container running

```bash
# 1) Generate Flask server code from your OpenAPI spec into APP_DIR
make generate-api

# 2) Build the Docker image from APP_DIR
make build-api

# 3) Run the container (bind-mounts APP_DIR for live edits)
make run-api

# (Optional) Tail logs in another terminal
make logs-api

# (Optional) Stop the container
make stop-api
```

Once `run-api` completes, the API is available at:

```
http://localhost:8080
```


## Optional: local Python environment with uv

These utilities are **only** for local development outside Docker. Docker is not required if you use them, but uv is.

```bash
# Create a virtualenv (reads .python_version if present; defaults to 3.12)
make venv-api

# Install Python dependencies into that venv
make install-api

# Activate it
source .venv/openapi-venv/bin/activate
```


## Common customizations (examples)

> For all available variables and their defaults, see `make help`.

* Use a different host port:

  ```bash
  make run-api PORT=9001
  ```

* Choose a different OpenAPI spec and pass generator options:

  ```bash
  make generate-api OPENAPI_SPEC=specs/petstore.yaml \
    OPENAPI_GEN_OPTS="--additional-properties packageName=my_api"
  ```

* Change image/container names:

  ```bash
  make build-api IMAGE_NAME=myorg/myapi
  make run-api CONTAINER_NAME=myapi-dev
  ```


## Cleanup

Remove only containers/images associated with this API:

```bash
make clean-api
```


## Tips

* If you change the OpenAPI spec, re-run `make generate-api` and `make build-api` before `make run-api`.
* Keep comments on **their own lines** when editing variable assignments in the Makefile. Inline comments after `VAR = value` are treated as part of the value by `make`.


## Need more?

Use:

```bash
make help
```

It shows all targets, what they do, and which variables you can override.
