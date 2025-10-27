# Contract Validation Report
**Date**: 2025-10-27 14:34:14
**Endpoints Validated**: 100

## Executive Summary
- ✅ Aligned: 0/100 endpoints (0%)
- ⚠️ Partial: 1/100 endpoints (1%)
- ❌ Misaligned: 32/100 endpoints (32%)

## Handler Validation Issues
- ⚠️ Missing required field checks: 404 handlers
- ⚠️ No type validation: 362 handlers
- ❌ Response structure mismatches: 68 handlers
- ✅ Proper Error model usage: 47 handlers

## Critical Mismatches (32 issues)

### 1. POST /auth - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | register, password, email, username |
| UI Code | password, username |
| API Impl | none |

**Missing in UI**: register, email

### 2. POST /user - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | phoneNumber, role, created, age, deleted, userId, modified, displayName, softDelete, email, familyId, userType |
| UI Code | none |
| API Impl | none |

**Missing in UI**: phoneNumber, role, created, age, deleted, userId, modified, displayName, softDelete, email, familyId, userType

### 3. PATCH /user/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | phoneNumber, role, created, age, deleted, userId, modified, displayName, softDelete, email, familyId, userType |
| UI Code | none |
| API Impl | none |

**Missing in UI**: phoneNumber, role, created, age, deleted, userId, modified, displayName, softDelete, email, familyId, userType

### 4. POST /user_details - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | userId, usage |
| UI Code | none |
| API Impl | none |

**Missing in UI**: userId, usage

### 5. PATCH /user_details/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | userId, usage |
| UI Code | none |
| API Impl | none |

**Missing in UI**: userId, usage

### 6. POST /convo_turn - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | contextWindow, contextSummary, temperature, message, sessionId, maxTokens, priority, animalId, metadata, moderationLevel |
| UI Code | none |
| API Impl | none |

**Missing in UI**: contextWindow, contextSummary, temperature, message, sessionId, maxTokens, priority, animalId, metadata, moderationLevel

### 7. POST /summarize_convo - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | summaryType, includeMetrics, includeTopics, sessionId, maxLength, includeSentiment, personalizationGoals |
| UI Code | none |
| API Impl | none |

**Missing in UI**: summaryType, includeMetrics, maxLength, personalizationGoals, includeSentiment, includeTopics, sessionId

### 8. POST /animal - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | status, name, species |
| UI Code | none |
| API Impl | none |

**Missing in UI**: name, species, status

### 9. PUT /animal/{animalId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | personality, status, description, species, name |
| UI Code | none |
| API Impl | none |

**Missing in UI**: personality, status, name, description, species

### 10. PATCH /animal_config - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | topP, personality, guardrails, aiModel, temperature, responseFormat, systemPrompt, guardrails.selected, guardrails.custom, voice, maxTokens, toolsEnabled |
| UI Code | none |
| API Impl | none |

**Missing in UI**: topP, personality, guardrails, aiModel, temperature, responseFormat, systemPrompt, guardrails.selected, guardrails.custom, voice, maxTokens, toolsEnabled

## Warnings (69 issues)

### 1. GET / - response_field_mismatch
**Severity**: medium

### 2. GET /admin - response_field_mismatch
**Severity**: medium

### 3. GET /member - response_field_mismatch
**Severity**: medium

### 4. POST /auth - response_field_mismatch
**Severity**: medium

### 5. POST /auth/refresh - response_field_mismatch
**Severity**: medium

### 6. POST /auth/reset_password - partial_field_mismatch
**Severity**: medium

### 7. GET /me - response_field_mismatch
**Severity**: medium

### 8. GET /user - response_field_mismatch
**Severity**: medium

### 9. GET /user/{userId} - response_field_mismatch
**Severity**: medium

### 10. PATCH /user/{userId} - response_field_mismatch
**Severity**: medium

## Recommendations

### High Priority
- Fix 32 misaligned endpoints immediately
- Add required field validation to 404 handlers
- Add contract validation to CI/CD pipeline

### Medium Priority
- Review 1 partially aligned endpoints
- Implement type checking in 362 handlers

### Low Priority
- Document null handling conventions
- Add integration tests for each endpoint
- Consider API versioning strategy
