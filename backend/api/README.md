# README
## TO DO:
* Add runbook documentation for the REST API, possibly under `docs/runbook/api`?
* Code
  + Use pagination correctly
  + Use machine generated models to avoid hardcoding them
  + Handle limiting queries

## Overview

This project implements a **Flask REST API** generated from an OpenAPI specification (`backend/api/openapi_spec.yaml`) and extended with custom logic.  
We use **openapi-generator** to scaffold machine-generated reference code, while keeping hand-written implementations separate under `backend/api/src/main/python/openapi_server/impl`.

DynamoDB is used for persistence (e.g., tables `quest-dev-user`, `quest-dev-family`, `quest-dev-animal`).

---

## Project Structure

```
backend/
  api/
    openapi_spec.yaml              # Source of truth for API contract
    generated/app/                 # Machine-generated code (DO NOT EDIT)
    src/main/python/openapi_server/
      controllers/                 # Thin routing layer, delegates to impl/
      impl/                        # Business logic implementations
      models/                      # Data models from OpenAPI schemas
      openapi/                     # OpenAPI spec mirror
```

---

## OpenAPI Spec Maintenance

- **Edit the contract first**:  
  Add new endpoints, schemas, and tags to `backend/api/openapi_spec.yaml`.

- **Visualize & validate**:  
  Copy/paste the spec into [Swagger Editor](https://editor.swagger.io/) for easier navigation and validation.

- **Testing from Swagger Editor**:  
  If calling your local API directly, select **Local server** in the dropdown at the top.

---

## Implementation Maintenance

1. **Regenerate machine code for reference**:
   ```bash
   make generate-api
   ```
   This updates the `backend/api/generated/app/` directory.

2. **Check for differences** (helps you see where generated code diverges from maintained code):
   ```bash
   diff -qr ./backend/api/src/main/python/openapi_server ./backend/api/generated/app/openapi_server/
   ```

3. **Keep specs in sync**:
   - `./backend/api/src/main/python/openapi_server/openapi/openapi.yaml`  
     should always match  
     `./backend/api/generated/app/openapi_server/openapi/openapi.yaml`.

4. **Keep models aligned**:
   - Example:  
     `backend/api/src/main/python/openapi_server/models/user.py` <--> generated equivalent.

---

## Running the API Locally

1. **Build and run with Make**:
   ```bash
   make clean-api build-api run-api logs-api
   ```
   - `clean-api` → removes old builds  
   - `build-api` → builds Docker image  
   - `run-api`   → starts container  
   - `logs-api`  → streams logs

2. **Test endpoints**:
   - Use [Swagger Editor](https://editor.swagger.io/)  
     - Paste in `backend/api/openapi_spec.yaml`  
     - Point to your local server (e.g. `http://localhost:8080`)  
   - Or use Postman / curl:
     ```bash
     curl -X GET http://localhost:8080/family
     ```

3. **Example POST request**:
   ```bash
   curl -X POST http://localhost:8080/family \
     -H 'Content-Type: application/json' \
     -d '{
           "familyId": "fam123",
           "parents": ["parent1@example.com"],
           "students": ["student1@example.com"]
         }'
   ```

---

## DynamoDB Notes

- By default, implementations expect DynamoDB tables:
  - `quest-dev-user`
  - `quest-dev-family`
  - `quest-dev-animal`
- Table names and region are configurable with environment variables:
  - `AWS_REGION` (default: `us-west-2`)
  - `DYNAMODB_ENDPOINT_URL` (set for LocalStack/dev)
  - `USER_TABLE_NAME`, `FAMILY_TABLE_NAME`, `ANIMAL_TABLE_NAME`

---

## Development Workflow (Recommended)

1. **Update the OpenAPI spec** → add endpoints/schemas.
2. **Generate reference code** with `make generate-api`.
3. **Compare differences** with `diff -qr ...`.
4. **Implement logic** in `impl/` modules.
5. **Run locally** with `make run-api`.
6. **Test** with Swagger Editor or Postman.
7. **Commit changes** only in `src/main/python/openapi_server` (never directly in `generated/app`).

---

## Tips for New Developers

- Always start from the **OpenAPI spec**; don’t hand-edit controllers or models directly.
- Controllers should stay **thin**; delegate to `impl/` functions (`handle_*` style).
- When regenerating code, don’t panic if many files show up in `generated/app/`—only reconcile changes needed in `src/main/python/openapi_server`.
- Use environment variables in `.env` or your shell to point the API to the right DynamoDB instance.
- Logs are your friend: `make logs-api` shows live requests hitting the service.
