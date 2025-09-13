#!/bin/bash
# /validate-frontend-backend-integration command
# Comprehensive frontend-to-backend integration validation with sequential reasoning

echo "🔍 Frontend-Backend Integration Validation"
echo "========================================="
echo ""
echo "This command performs systematic validation of the complete integration chain:"
echo "Frontend UI → Authentication → API → DynamoDB → Data Display"
echo ""
echo "Use this prompt with Claude Code:"
echo ""
cat << 'EOF'
/validate-frontend-backend-integration

Validate complete frontend-to-backend integration for animal management using sequential reasoning with comprehensive test planning, diagnosis, and user experience matching.

## Required Process - Use Sequential Reasoning MCP Throughout
**CRITICAL**: Use sequential reasoning MCP for ALL steps including test planning, execution, and diagnosis.

## Pre-Step: User Experience Test Plan Creation
**Sequential Reasoning**: Design test plan that exactly matches real user interaction patterns
- Analyze frontend routing structure and component hierarchy
- Map expected user journey: Login → Dashboard → Animal Management → Chatbot Personalities
- Identify exact UI element selectors, button texts, and navigation paths
- Plan Playwright interactions that mirror genuine user clicks, typing, and navigation
- Predict potential UI loading delays, async operations, and state changes
- Design assertions that validate actual visual elements users would see
- Account for responsive design, accessibility features, and browser compatibility

## Validation Steps

### Step 1: Service Status Verification
**Sequential Reasoning**: Plan systematic service health validation approach
- Verify frontend running on http://localhost:3000 with health checks
- Verify backend running on http://localhost:8080 with API endpoint tests
- Check Docker container status and logs for backend API
- Verify Vite development server status and hot reload functionality
- Test basic connectivity: frontend → backend proxy configuration

### Step 2: Backend Data Structure Analysis
**Sequential Reasoning**: Deep analysis of data flow and schema expectations
- Examine `openapi_server/models/animal.py` for complete OpenAPI Animal model
- Review `openapi_server/impl/animals.py` for data transformation logic
- Analyze `openapi_server/impl/utils/orm/dynamo.py` for field mapping patterns
- Study hexagonal architecture: DynamoDB → Domain Objects → OpenAPI Models → JSON
- Document exact field names, data types, required properties, and validation rules
- Map data transformation pipeline and identify potential failure points

### Step 2.2: Animal Configuration Structure Validation
**Sequential Reasoning**: Design configurations matching exact backend requirements
- Create 3 animal configurations based on Step 2 analysis
- Include ALL required OpenAPI fields: animalId, name, species, status
- Add proper audit structure: created.at, created.by, modified.at, modified.by
- Include chatbot-specific fields: personality, configuration, AI model settings
- Validate against schema constraints: status enums, date formats, actor structure
- Ensure data types match backend expectations exactly

### Step 3: DynamoDB Data Population Verification
**Sequential Reasoning**: Comprehensive data layer validation
- AWS CLI scan quest-dev-animal table with complete field analysis
- Verify field naming consistency: animalId vs animal_id mapping issues
- Count animals with active status and validate data completeness
- Check for orphaned records, missing required fields, or malformed data
- Validate timestamp formats and actor object structures

### Step 4: Backend API Data Retrieval Validation
**Sequential Reasoning**: End-to-end API testing with error analysis
- Test authentication flow: POST /auth with comprehensive error checking
- Test animal retrieval: GET /animal_list with token validation
- Analyze response structure against OpenAPI specification exactly
- Document field mapping discrepancies and transformation failures
- Test error scenarios: invalid tokens, malformed data, network issues
- Validate HTTP status codes, error messages, and response formats

### Step 5: Frontend Authentication Validation
**Sequential Reasoning**: Complete UI authentication workflow testing
- Use Playwright to navigate to http://localhost:3000 exactly as user would
- Test login form interaction: field focus, typing, form submission
- Verify visual feedback: loading states, error messages, success redirects
- Check localStorage token persistence and session management
- Test protected route behavior and unauthorized access handling

### Step 6: UI Navigation to Animal Management (User Experience Critical)
**Sequential Reasoning**: Playwright automation matching genuine user experience
- Start from authenticated dashboard as real user would see it
- Identify exact navigation elements: menus, buttons, links by visible text
- Click through navigation: Dashboard → Animal Management → Chatbot Personalities
- Wait for page loads, async API calls, and UI state changes
- Validate that each page renders completely before proceeding
- Screenshot actual UI state at each step for visual validation
- Check for any loading spinners, error states, or broken layouts

### Step 7: Animal Data Display Verification (Critical User Experience Match)
**Sequential Reasoning**: Validate actual user-visible data presentation
- Use Playwright to inspect rendered animal list exactly as user sees it
- Verify animal names, species, status display in actual UI components
- Check API network calls in browser DevTools during UI interaction
- Validate that DynamoDB data appears correctly in user interface
- Test filtering, sorting, search functionality if present
- Ensure UI handles empty states, loading states, and error states properly

## Output Requirements

### If COMPLETE SUCCESS:
- **Status**: ✅ COMPLETE SUCCESS
- **Summary**: All integration points validated successfully
- **Evidence**: Screenshots, API response samples, UI verification screenshots

### If PROBLEMS DETECTED:
**Sequential Reasoning**: Produce comprehensive diagnostic analysis

#### **Status**: ❌ INTEGRATION FAILURES DETECTED

#### **Detailed Failure Analysis**:
- **Root Cause**: Exact technical issue identified
- **Impact**: User experience consequences
- **Evidence**: Screenshots, error logs, API responses, network traces

#### **Reproduction Steps**:
1. Exact commands/clicks to reproduce the issue
2. Expected vs actual behavior at each step
3. Browser console errors, network failures, or API errors
4. Visual evidence of UI problems or data display issues

#### **Failure Criteria Met**:
- Specific validation that failed (e.g., "Animal list API returns 400 due to field mapping")
- User experience impact (e.g., "User sees blank animal list instead of 8 animals")

#### **Success Criteria Not Met**:
- What should happen vs what actually happens
- Specific user workflows that are broken
- Data flow interruptions in the integration pipeline

## Critical Requirements
- **Playwright Usage**: Must match actual user clicks, waits, and visual validation
- **Real User Experience**: Test what users actually see and interact with
- **No Fixing**: Only test, validate, diagnose - do not attempt repairs
- **Evidence-Based**: Include screenshots, logs, API responses as proof
- **Sequential Reasoning**: Use for every analysis and decision point

## Context
- CMZ chatbot backend API using OpenAPI-first development
- React frontend with Vite proxy to Flask/Connexion backend
- DynamoDB persistence with hexagonal architecture
- JWT authentication with role-based access
- User experience must match actual browser interaction patterns
EOF

echo ""
echo "📋 Usage: Copy the prompt above and paste it into Claude Code"
echo "🎯 Purpose: Comprehensive integration validation with user experience matching"
echo "⚡ Requirements: Sequential reasoning MCP, Playwright for UI testing"