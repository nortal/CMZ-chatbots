# Contract Validation Report
**Date**: 2025-10-11 20:55:40
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
| OpenAPI | register, email, username, password |
| UI Code | password, username |
| API Impl | none |

**Missing in UI**: register, email

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
| OpenAPI | email, familyId, softDelete, age, userId, role, deleted, userType, displayName, modified, created, phoneNumber |
| UI Code | none |
| API Impl | none |

**Missing in UI**: email, familyId, softDelete, age, userId, role, deleted, userType, displayName, modified, created, phoneNumber

### 4. PATCH /user/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | email, familyId, softDelete, age, userId, role, deleted, userType, displayName, modified, created, phoneNumber |
| UI Code | none |
| API Impl | none |

**Missing in UI**: email, familyId, softDelete, age, userId, role, deleted, userType, displayName, modified, created, phoneNumber

### 5. POST /user_details - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | usage, userId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: userId, usage

### 6. PATCH /user_details/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | usage, userId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: userId, usage

### 7. POST /convo_turn - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | animalId, moderationLevel, temperature, message, priority, contextSummary, sessionId, contextWindow, metadata, maxTokens |
| UI Code | none |
| API Impl | none |

**Missing in UI**: animalId, moderationLevel, temperature, message, priority, contextSummary, sessionId, contextWindow, metadata, maxTokens

### 8. POST /summarize_convo - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | includeTopics, maxLength, includeMetrics, includeSentiment, summaryType, sessionId, personalizationGoals |
| UI Code | none |
| API Impl | none |

**Missing in UI**: includeTopics, summaryType, sessionId, maxLength, includeMetrics, includeSentiment, personalizationGoals

### 9. POST /animal - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | species, status, name |
| UI Code | none |
| API Impl | none |

**Missing in UI**: species, status, name

### 10. PUT /animal/{animalId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | species, status, name, personality |
| UI Code | none |
| API Impl | none |

**Missing in UI**: species, status, name, personality

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
