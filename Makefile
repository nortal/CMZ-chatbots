# =========================
# Configurable variables
# =========================

# Name/tag for the Docker image and container
IMAGE_NAME ?= cmz-openapi-api
CONTAINER_NAME ?= $(IMAGE_NAME)-dev

# OpenAPI spec and app paths (relative to repo root)
OPENAPI_SPEC ?= backend/api/openapi_spec.yaml
SRC_APP_DIR ?= backend/api/src/main/python
GEN_APP_DIR ?= backend/api/generated/app
REQUIREMENTS_FILE ?= $(SRC_APP_DIR)/requirements.txt

# Where to stash backups of existing code before regeneration
GEN_TMP_BASE ?= tmp

# Network / ports
# host port to expose the app on (8080 by default)
PORT ?= 8080
CONTAINER_PORT ?= 8080

# OpenAPI Generator image + generator choice
OPENAPI_GEN_IMAGE ?= openapitools/openapi-generator-cli:latest
OPENAPI_GENERATOR ?= python-flask

# Optional extra OpenAPI generator opts (space-separated)
OPENAPI_GEN_OPTS ?=

# ----- Local Python tooling (UV virtualenv) -----
UV ?= uv
PYTHON_VERSION ?= $(shell cat .python_version 2>/dev/null || echo 3.12)
VENV_DIR ?= .venv/openapi-venv

# =========================
# Helpers
# =========================

ROOT_DIR := $(shell pwd)

# Label to tag images/containers so we can clean up safely
API_LABEL_KEY := io.cmz.api
API_LABEL_VAL := $(IMAGE_NAME)
API_LABEL := $(API_LABEL_KEY)=$(API_LABEL_VAL)

$(GEN_TMP_BASE):
	@mkdir -p "$(GEN_TMP_BASE)"

.PHONY: help
help:
	@echo "Targets (API-specific):"
	@echo "  generate-api     Backup $(GEN_APP_DIR) to tmp/api_<timestamp> and regenerate Flask code from $(OPENAPI_SPEC)"
	@echo "  build-api        Build Docker image $(IMAGE_NAME) from generated Dockerfile in $(SRC_APP_DIR)"
	@echo "  run-api          Run container $(CONTAINER_NAME) with $(SRC_APP_DIR) mounted; port $(PORT)->$(CONTAINER_PORT)"
	@echo "  stop-api         Stop container $(CONTAINER_NAME) if running"
	@echo "  logs-api         Tail logs from $(CONTAINER_NAME)"
	@echo "  clean-api        Remove ONLY containers/images labeled $(API_LABEL) (and image named $(IMAGE_NAME))"
	@echo ""
	@echo "Local dev with UV:"
	@echo "  venv-api         Create UV virtualenv at $(VENV_DIR) (Python $(PYTHON_VERSION))"
	@echo "  rebuild-venv-api Delete and recreate virtualenv at $(VENV_DIR) (calls venv-api)"
	@echo "  install-api      Install pip requirements from $(REQUIREMENTS_FILE) into $(VENV_DIR)"
	@echo ""
	@echo "Variables (override like VAR=value make <target>):"
	@echo "  IMAGE_NAME, CONTAINER_NAME, OPENAPI_SPEC, GEN_APP_DIR, SRC_APP_DIR, GEN_TMP_BASE, PORT, CONTAINER_PORT"
	@echo "  OPENAPI_GEN_IMAGE, OPENAPI_GENERATOR, OPENAPI_GEN_OPTS, UV, PYTHON_VERSION, VENV_DIR"

# =========================
# 1) Generate Flask code from OpenAPI spec (with backup)
# =========================
.PHONY: generate-api
generate-api: $(GEN_TMP_BASE)
	@set -e; \
	echo ">> Backing up existing app directory (if any)"; \
	TS=$$(date +%Y%m%d_%H%M%S); \
	BACKUP_DIR="$(GEN_TMP_BASE)/api_$${TS}"; \
	mkdir -p "$${BACKUP_DIR}"; \
	if [ -d "$(GEN_APP_DIR)" ]; then \
		echo "   - Copying '$(GEN_APP_DIR)' -> '$${BACKUP_DIR}/app'"; \
		cp -a "$(GEN_APP_DIR)" "$${BACKUP_DIR}/app"; \
	else \
		echo "   - No existing '$(GEN_APP_DIR)' directory found; skipping copy"; \
	fi; \
	echo ">> Generating code from '$(OPENAPI_SPEC)' into '$(GEN_APP_DIR)' using generator '$(OPENAPI_GENERATOR)'"; \
	mkdir -p "$(GEN_APP_DIR)"; \
	docker run --rm \
		-v "$(ROOT_DIR)":/local \
		"$(OPENAPI_GEN_IMAGE)" generate \
		-g "$(OPENAPI_GENERATOR)" \
		-i "/local/$(OPENAPI_SPEC)" \
		-o "/local/$(GEN_APP_DIR)" \
		$(OPENAPI_GEN_OPTS); \
	echo ">> Generation complete."

# =========================
# 2) Build Docker image
# =========================
.PHONY: build-api
build-api:
	@set -e; \
	if [ ! -f "$(SRC_APP_DIR)/Dockerfile" ]; then \
		echo "ERROR: Dockerfile not found at '$(SRC_APP_DIR)/Dockerfile'. Run 'make generate-api' first."; \
		exit 1; \
	fi; \
	echo ">> Building Docker image '$(IMAGE_NAME)' from '$(SRC_APP_DIR)'"; \
	docker build \
		--label "$(API_LABEL)" \
		-t "$(IMAGE_NAME)" \
		"$(SRC_APP_DIR)"

# =========================
# 3) Run Docker container (with live bind mount)
# =========================
.PHONY: run-api
run-api:
	@set -e; \
	echo ">> Starting container '$(CONTAINER_NAME)' from image '$(IMAGE_NAME)'"; \
	if [ "$(DEBUG)" = "1" ]; then \
		echo ">> Running in DEBUG mode (interactive, Flask debug enabled)"; \
		docker run --rm -it \
			--label "$(API_LABEL)" \
			--name "$(CONTAINER_NAME)" \
			-p "$(PORT):$(CONTAINER_PORT)" \
			-v "$(ROOT_DIR)/$(SRC_APP_DIR)":/app \
			-v $$HOME/.aws:/root/.aws:ro \
			-e FLASK_ENV=development \
			"$(IMAGE_NAME)"; \
	else \
		docker run --rm -d \
			--label "$(API_LABEL)" \
			--name "$(CONTAINER_NAME)" \
			-p "$(PORT):$(CONTAINER_PORT)" \
			-v "$(ROOT_DIR)/$(SRC_APP_DIR)":/app \
			-v $$HOME/.aws:/root/.aws:ro \
			"$(IMAGE_NAME)"; \
		echo ">> Container running: http://localhost:$(PORT)"; \
	fi

.PHONY: stop-api
stop-api:
	@set -e; \
	if [ -n "$$(docker ps -q -f name=^/$(CONTAINER_NAME)$$)" ]; then \
		echo ">> Stopping container '$(CONTAINER_NAME)'"; \
		docker stop "$(CONTAINER_NAME)" >/dev/null; \
	else \
		echo ">> No running container named '$(CONTAINER_NAME)'"; \
	fi

.PHONY: logs-api
logs-api:
	@docker logs -f "$(CONTAINER_NAME)"

# =========================
# 4) Clean ONLY this API's containers & images
# =========================
.PHONY: clean-api
clean-api:
	@set -e; \
	echo ">> Removing containers labeled $(API_LABEL)"; \
	CONTAINERS=$$(docker ps -a -q --filter "label=$(API_LABEL)"); \
	if [ -n "$${CONTAINERS}" ]; then \
		docker rm -f $${CONTAINERS}; \
	else \
		echo "   - No containers to remove"; \
	fi; \
	echo ">> Removing images labeled $(API_LABEL) OR named '$(IMAGE_NAME)'"; \
	IMAGES_LABELED=$$(docker images -q --filter "label=$(API_LABEL)"); \
	IMAGES_NAMED=$$(docker images -q "$(IMAGE_NAME)"); \
	IMAGES=$$(printf "%s\n%s\n" "$${IMAGES_LABELED}" "$${IMAGES_NAMED}" | sort -u); \
	if [ -n "$${IMAGES}" ]; then \
		docker rmi -f $${IMAGES}; \
	else \
		echo "   - No images to remove"; \
	fi

# =========================
# 5) Local dev: UV virtualenv + install
# =========================
.PHONY: venv-api
venv-api:
	@set -e; \
	if ! command -v "$(UV)" >/dev/null 2>&1; then \
		echo "ERROR: 'uv' not found. Install from https://docs.astral.sh/uv/"; \
		exit 1; \
	fi; \
	echo ">> Creating UV virtualenv at '$(VENV_DIR)' (Python $(PYTHON_VERSION))"; \
	mkdir -p "$(dir $(VENV_DIR))"; \
	"$(UV)" venv --python "$(PYTHON_VERSION)" "$(VENV_DIR)"; \
	echo ">> Done. Activate with:"; \
	echo "   source $(VENV_DIR)/bin/activate"

.PHONY: rebuild-venv-api
rebuild-venv-api:
	@set -e; \
	if [ -d "$(VENV_DIR)" ]; then \
		echo ">> Removing existing virtualenv at '$(VENV_DIR)'"; \
		rm -rf "$(VENV_DIR)"; \
	else \
		echo ">> No existing virtualenv found at '$(VENV_DIR)'"; \
	fi; \
	$(MAKE) venv-api

.PHONY: install-api
install-api: venv-api
	@set -e; \
	if [ ! -f "$(REQUIREMENTS_FILE)" ]; then \
		echo "ERROR: Requirements file not found at '$(REQUIREMENTS_FILE)'. Run 'make generate-api' first."; \
		exit 1; \
	fi; \
	if ! command -v "$(UV)" >/dev/null 2>&1; then \
		echo "ERROR: 'uv' not found. Install from https://docs.astral.sh/uv/"; \
		exit 1; \
	fi; \
	echo ">> Installing Python packages from '$(REQUIREMENTS_FILE)' into '$(VENV_DIR)'"; \
	"$(UV)" pip install -r "$(REQUIREMENTS_FILE)" -p "$(VENV_DIR)/bin/python"; \
	echo ">> Installed. Activate with: source $(VENV_DIR)/bin/activate"
