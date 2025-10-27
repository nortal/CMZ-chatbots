# Contract Validation Report
**Date**: 2025-10-11 20:54:25
**Endpoints Validated**: 61

## Executive Summary
- ✅ Aligned: 0/61 endpoints (0%)
- ⚠️ Partial: 0/61 endpoints (0%)
- ❌ Misaligned: 19/61 endpoints (31%)

## Handler Validation Issues
- ⚠️ Missing required field checks: 260 handlers
- ⚠️ No type validation: 236 handlers
- ❌ Response structure mismatches: 42 handlers
- ✅ Proper Error model usage: 10 handlers

## Critical Mismatches (19 issues)

### 1. POST /auth - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | email, password, username, register |
| UI Code | none |
| API Impl | none |

**Missing in UI**: email, password, username, register

### 2. POST /auth/reset_password - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | email |
| UI Code | none |
| API Impl | none |

**Missing in UI**: email

### 3. POST /user - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | role, softDelete, userId, phoneNumber, created, modified, displayName, familyId, email, age, deleted, userType |
| UI Code | none |
| API Impl | none |

**Missing in UI**: role, softDelete, userId, phoneNumber, created, modified, displayName, familyId, email, age, deleted, userType

### 4. PATCH /user/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | role, softDelete, userId, phoneNumber, created, modified, displayName, familyId, email, age, deleted, userType |
| UI Code | none |
| API Impl | none |

**Missing in UI**: role, softDelete, userId, phoneNumber, created, modified, displayName, familyId, email, age, deleted, userType

### 5. POST /user_details - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | usage, userId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: usage, userId

### 6. PATCH /user_details/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | usage, userId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: usage, userId

### 7. POST /convo_turn - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | sessionId, animalId, message, moderationLevel, contextWindow, temperature, maxTokens, contextSummary, metadata, priority |
| UI Code | none |
| API Impl | none |

**Missing in UI**: sessionId, animalId, message, moderationLevel, contextWindow, temperature, maxTokens, contextSummary, metadata, priority

### 8. POST /summarize_convo - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | sessionId, maxLength, personalizationGoals, summaryType, includeMetrics, includeTopics, includeSentiment |
| UI Code | none |
| API Impl | none |

**Missing in UI**: sessionId, maxLength, includeMetrics, personalizationGoals, includeTopics, includeSentiment, summaryType

### 9. POST /animal - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | name, species, status |
| UI Code | none |
| API Impl | none |

**Missing in UI**: name, species, status

### 10. PUT /animal/{animalId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | name, species, status, personality |
| UI Code | none |
| API Impl | none |

**Missing in UI**: name, species, status, personality

## Warnings (42 issues)

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

### 6. GET /me - response_field_mismatch
**Severity**: medium

### 7. GET /user - response_field_mismatch
**Severity**: medium

### 8. GET /user/{userId} - response_field_mismatch
**Severity**: medium

### 9. PATCH /user/{userId} - response_field_mismatch
**Severity**: medium

### 10. GET /user_details - response_field_mismatch
**Severity**: medium

## Recommendations

### High Priority
- Fix 19 misaligned endpoints immediately
- Add required field validation to 260 handlers
- Add contract validation to CI/CD pipeline

### Medium Priority
- Implement type checking in 236 handlers

### Low Priority
- Document null handling conventions
- Add integration tests for each endpoint
- Consider API versioning strategy
