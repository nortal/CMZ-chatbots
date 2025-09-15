# Jira Story: Implement PUT /animal/{id} Endpoint for Animal Management

## Story: Enable Admin and Zookeeper Animal Information Updates

**Summary**: Implement PUT /animal/{id} endpoint to allow administrators and zookeepers to update animal information (name, species, status) with proper validation and persistence

**Issue Type**: Story
**Parent Epic**: PR003946-61 (CMZ API Validation)
**Story Points**: 5
**Priority**: High
**Labels**: api, backend, persistence, animal-management, crud
**Billable**: Billable
**Components**: Backend API, DynamoDB Integration

**Description**:
As an administrator or zookeeper, I want to update animal information (name, species, and status) through the API so that I can maintain accurate animal records without needing direct database access.

### Background
The Animal Config dialog in the frontend attempts to update both Animal basic information (name, species, status) and Animal Configuration (personality, AI settings) when saving. Currently, the PUT /animal/{id} endpoint is not implemented, causing animal name and species updates to fail with a 500 error. This results in a poor user experience where changes appear to save but immediately revert.

### Technical Context
- **Current State**: Endpoint defined in OpenAPI spec but returns 501 Not Implemented
- **Code Generation Issue**: Generated controller has malformed function signature (missing comma between parameters)
- **Frontend Integration**: Frontend already calls this endpoint via `updateAnimal()` function
- **Database**: DynamoDB table `quest-dev-animal` with animalId as primary key
- **Related Endpoint**: PATCH /animal_config (working correctly for configuration updates)

### Implementation Requirements

#### Field Specifications
- **name**:
  - Type: string
  - Required: No (partial updates allowed)
  - Min Length: 1 character
  - Max Length: 100 characters
  - Validation: No special characters that could cause XSS
  - Example: "Leo the Lion", "Bella the Bear"

- **species**:
  - Type: string
  - Required: No (partial updates allowed)
  - Min Length: 1 character
  - Max Length: 100 characters
  - Validation: Scientific naming convention preferred
  - Example: "Panthera leo", "Ursus americanus"

- **status**:
  - Type: string (enum)
  - Required: No (partial updates allowed)
  - Allowed Values: "active", "hidden"
  - Default: No change if not provided
  - Example: "active"

- **animalId**:
  - Type: string
  - Required: Yes (path parameter)
  - Immutable: CANNOT be changed via PUT
  - Used as: Primary key for database lookup
  - Validation: Must exist in database

### Acceptance Criteria

**AC1: Endpoint Implementation**
- **Given** a valid animalId exists in the database
- **When** PUT request is made to `/animal/{id}` with partial or complete update data
- **Then** the endpoint updates only the provided fields
- **And** returns the complete updated Animal object with 200 status
- **Test**: `curl -X PUT http://localhost:8080/animal/leo_001 -H "Content-Type: application/json" -d '{"name":"King Leo"}'`
- **Verification**: Response contains updated name while species and status remain unchanged

**AC2: Field Validation**
- **Given** a PUT request with field data
- **When** name or species exceeds 100 characters OR is empty string
- **Then** return 422 Validation Error with specific field error details
- **Test**: `curl -X PUT http://localhost:8080/animal/leo_001 -d '{"name":""}' | jq '.code'` returns "validation_error"
- **Verification**: Error message specifies "name: minimum length is 1"

**AC3: Partial Update Support**
- **Given** an existing animal with name="Leo", species="Panthera leo", status="active"
- **When** PUT request contains only `{"species":"Panthera leo africana"}`
- **Then** only species is updated, name and status remain unchanged
- **Test**: Update one field, verify others unchanged in DynamoDB
- **Verification**: `aws dynamodb get-item --table-name quest-dev-animal --key '{"animalId":{"S":"leo_001"}}'` shows only species changed

**AC4: AnimalId Immutability**
- **Given** a PUT request to `/animal/{id}`
- **When** request body contains `{"animalId":"different_id"}`
- **Then** animalId in the body is ignored, path parameter is used
- **And** animalId in database remains unchanged
- **Test**: `curl -X PUT http://localhost:8080/animal/leo_001 -d '{"animalId":"new_id","name":"Leo"}'`
- **Verification**: Response and database still show animalId as "leo_001"

**AC5: Non-Existent Animal Handling**
- **Given** an animalId that doesn't exist in the database
- **When** PUT request is made to `/animal/{non_existent_id}`
- **Then** return 404 Not Found with appropriate error message
- **Test**: `curl -X PUT http://localhost:8080/animal/fake_id -d '{"name":"Test"}' | jq '.code'` returns "not_found"
- **Verification**: Error message states "Animal with id 'fake_id' not found"

**AC6: Audit Trail Updates**
- **Given** a successful animal update
- **When** the update is persisted to DynamoDB
- **Then** the `modified.at` timestamp is updated to current UTC time
- **And** the `modified.by` contains the user information (when auth is implemented)
- **Test**: Compare modified.at before and after update
- **Verification**: `modified.at` timestamp is more recent than before update

**AC7: Status Enum Validation**
- **Given** a PUT request with status field
- **When** status value is not "active" or "hidden"
- **Then** return 422 Validation Error
- **Test**: `curl -X PUT http://localhost:8080/animal/leo_001 -d '{"status":"invalid"}'`
- **Verification**: Error message states "status: must be one of ['active', 'hidden']"

**AC8: Integration with Animal Config Dialog**
- **Given** the Animal Config dialog in the frontend
- **When** user updates Animal Name and/or Species and clicks Save
- **Then** the PUT /animal/{id} endpoint successfully updates the fields
- **And** the updated values persist in the UI after save
- **And** the values remain after closing and reopening the dialog
- **Test**: Use Playwright to update fields and verify persistence
- **Verification**: Fields don't revert to original values after save

**AC9: Concurrent Update Handling**
- **Given** two simultaneous PUT requests for the same animal
- **When** both requests attempt to update different fields
- **Then** both updates should be applied without data corruption
- **Test**: Parallel curl requests updating different fields
- **Verification**: Final state in DynamoDB contains both updates

**AC10: Empty Request Body Handling**
- **Given** a PUT request with empty body `{}`
- **When** the request is processed
- **Then** return 200 with unchanged animal data (no-op)
- **Test**: `curl -X PUT http://localhost:8080/animal/leo_001 -d '{}'`
- **Verification**: Response shows animal data unchanged

### Implementation Notes

1. **Fix Code Generation**: Update the generated controller function signature from `def animal_id_put(idanimal_update):` to `def animal_id_put(id, animal_update):`

2. **Implementation Location**: `/backend/api/src/main/python/openapi_server/impl/animals.py` - implement `handle_animal_id_put()` function

3. **DynamoDB Operations**: Use existing utilities from `impl/utils/dynamo.py` for consistent error handling and audit trails

4. **Testing**: Create unit tests in `/backend/api/src/main/python/openapi_server/test/test_animals_controller.py`

### Definition of Done
- [ ] Endpoint implementation complete in `impl/animals.py`
- [ ] Code generation issue fixed in controller
- [ ] All acceptance criteria pass
- [ ] Unit tests achieve >90% coverage
- [ ] Integration tests pass with both DynamoDB and file persistence modes
- [ ] Frontend Animal Config dialog successfully updates animal name and species
- [ ] API documentation updated if needed
- [ ] Code reviewed and approved
- [ ] No security vulnerabilities introduced

### Test Data
Use existing test animal for validation:
- animalId: "leo_001"
- name: "Leo the Lion"
- species: "Panthera leo"
- status: "active"

### Security Considerations
- Input validation to prevent XSS attacks
- Field length limits to prevent buffer overflow
- No SQL/NoSQL injection vulnerabilities (use parameterized queries)
- Audit trail for compliance tracking
- Future: Role-based access control (admin/zookeeper only)

### Dependencies
- OpenAPI spec already defines the endpoint
- Frontend already has the updateAnimal() function ready
- DynamoDB table and utilities are in place
- No external service dependencies

### Estimated Effort
**5 Story Points** breakdown:
- 1 point: Fix code generation issue
- 2 points: Implement endpoint with validation
- 1 point: Write comprehensive unit tests
- 1 point: Integration testing and frontend validation

### Related Tickets
- Parent Epic: PR003946-61 (CMZ API Validation)
- Related: Animal Config Dialog Implementation
- Blocks: Full Animal Management CRUD functionality