# Contract Validation Report
**Date**: 2025-10-11 20:56:46
**Endpoints Validated**: 61

## Executive Summary
- ✅ Aligned: 0/61 endpoints (0%)
- ⚠️ Partial: 1/61 endpoints (2%)
- ❌ Misaligned: 18/61 endpoints (30%)

## Handler Validation Issues
- ⚠️ Missing required field checks: 260 handlers
- ⚠️ No type validation: 236 handlers
- ❌ Response structure mismatches: 42 handlers
- ✅ Proper Error model usage: 10 handlers

## Critical Mismatches (18 issues)

### 1. POST /auth - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | email, register, username, password |
| UI Code | username, password |
| API Impl | none |

**Missing in UI**: email, register

### 2. POST /user - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | age, displayName, created, softDelete, email, familyId, modified, phoneNumber, userType, deleted, role, userId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: age, displayName, created, softDelete, email, familyId, modified, phoneNumber, userType, deleted, role, userId

### 3. PATCH /user/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | age, displayName, created, softDelete, email, familyId, modified, phoneNumber, userType, deleted, role, userId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: age, displayName, created, softDelete, email, familyId, modified, phoneNumber, userType, deleted, role, userId

### 4. POST /user_details - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | usage, userId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: usage, userId

### 5. PATCH /user_details/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | usage, userId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: usage, userId

### 6. POST /convo_turn - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | maxTokens, message, sessionId, contextSummary, animalId, temperature, metadata, priority, moderationLevel, contextWindow |
| UI Code | none |
| API Impl | none |

**Missing in UI**: maxTokens, message, sessionId, contextSummary, animalId, temperature, metadata, priority, moderationLevel, contextWindow

### 7. POST /summarize_convo - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | maxLength, includeSentiment, summaryType, sessionId, includeTopics, includeMetrics, personalizationGoals |
| UI Code | none |
| API Impl | none |

**Missing in UI**: sessionId, includeTopics, includeSentiment, maxLength, includeMetrics, summaryType, personalizationGoals

### 8. POST /animal - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | species, name, status |
| UI Code | none |
| API Impl | none |

**Missing in UI**: species, name, status

### 9. PUT /animal/{animalId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | species, name, personality, status |
| UI Code | none |
| API Impl | none |

**Missing in UI**: species, name, personality, status

### 10. PATCH /animal_config - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | maxTokens, guardrails.custom, guardrails, personality, toolsEnabled, guardrails.selected, topP, aiModel, responseFormat, temperature, voice |
| UI Code | none |
| API Impl | none |

**Missing in UI**: maxTokens, guardrails.custom, guardrails, personality, toolsEnabled, guardrails.selected, topP, aiModel, responseFormat, temperature, voice

## Warnings (43 issues)

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
- Fix 18 misaligned endpoints immediately
- Add required field validation to 260 handlers
- Add contract validation to CI/CD pipeline

### Medium Priority
- Review 1 partially aligned endpoints
- Implement type checking in 236 handlers

### Low Priority
- Document null handling conventions
- Add integration tests for each endpoint
- Consider API versioning strategy
