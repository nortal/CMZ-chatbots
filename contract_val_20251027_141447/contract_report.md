# Contract Validation Report
**Date**: 2025-10-27 14:14:48
**Endpoints Validated**: 100

## Executive Summary
- ✅ Aligned: 0/100 endpoints (0%)
- ⚠️ Partial: 1/100 endpoints (1%)
- ❌ Misaligned: 32/100 endpoints (32%)

## Handler Validation Issues
- ⚠️ Missing required field checks: 382 handlers
- ⚠️ No type validation: 340 handlers
- ❌ Response structure mismatches: 68 handlers
- ✅ Proper Error model usage: 47 handlers

## Critical Mismatches (32 issues)

### 1. POST /auth - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | password, register, email, username |
| UI Code | password, username |
| API Impl | none |

**Missing in UI**: register, email

### 2. POST /user - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | displayName, familyId, phoneNumber, created, age, deleted, softDelete, role, userId, modified, email, userType |
| UI Code | none |
| API Impl | none |

**Missing in UI**: displayName, familyId, phoneNumber, created, age, deleted, softDelete, role, userId, modified, email, userType

### 3. PATCH /user/{userId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | displayName, familyId, phoneNumber, created, age, deleted, softDelete, role, userId, modified, email, userType |
| UI Code | none |
| API Impl | none |

**Missing in UI**: displayName, familyId, phoneNumber, created, age, deleted, softDelete, role, userId, modified, email, userType

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
| OpenAPI | contextWindow, message, metadata, maxTokens, temperature, contextSummary, animalId, sessionId, priority, moderationLevel |
| UI Code | none |
| API Impl | none |

**Missing in UI**: contextWindow, message, metadata, maxTokens, temperature, contextSummary, animalId, sessionId, priority, moderationLevel

### 7. POST /summarize_convo - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | includeMetrics, maxLength, summaryType, includeSentiment, personalizationGoals, includeTopics, sessionId |
| UI Code | none |
| API Impl | none |

**Missing in UI**: includeTopics, includeMetrics, maxLength, summaryType, sessionId, includeSentiment, personalizationGoals

### 8. POST /animal - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | name, status, species |
| UI Code | none |
| API Impl | none |

**Missing in UI**: name, status, species

### 9. PUT /animal/{animalId} - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | name, status, species, personality, description |
| UI Code | none |
| API Impl | none |

**Missing in UI**: name, status, species, personality, description

### 10. PATCH /animal_config - field_mismatch
**Layer**: request

| Source | Fields |
|--------|--------|
| OpenAPI | toolsEnabled, aiModel, guardrails.custom, responseFormat, maxTokens, guardrails.selected, temperature, guardrails, topP, systemPrompt, personality, voice |
| UI Code | none |
| API Impl | none |

**Missing in UI**: toolsEnabled, aiModel, guardrails.custom, responseFormat, maxTokens, guardrails.selected, temperature, guardrails, topP, systemPrompt, personality, voice

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
- Add required field validation to 382 handlers
- Add contract validation to CI/CD pipeline

### Medium Priority
- Review 1 partially aligned endpoints
- Implement type checking in 340 handlers

### Low Priority
- Document null handling conventions
- Add integration tests for each endpoint
- Consider API versioning strategy
