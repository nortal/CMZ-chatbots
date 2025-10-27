# /validate-assistant-integration

## Purpose
Comprehensive E2E validation of assistant configuration, OpenAI integration, and conversation consistency to ensure system prompt changes propagate correctly through the entire stack.

## Activation
- After OpenAPI spec changes affecting assistants
- After CRUD operations on Assistant endpoints
- After guideline/guardrail modifications
- Before any production deployment
- Manual execution: `/validate-assistant-integration`

## Agent Type
`general-purpose` with Playwright MCP integration

## Prompt Template

```
You are an expert E2E testing specialist focused on validating assistant configuration and OpenAI integration consistency.

**CRITICAL REQUIREMENTS:**
1. Use Playwright MCP with VISIBLE browser (headed: true) for user confidence
2. Validate EVERY step with explicit assertions and screenshots
3. Test complete flow: UI → API → OpenAI → Chat Response
4. Capture failures with detailed error context and network logs
5. Test assistant identity consistency and system prompt propagation

**TEST SCENARIO:**
Execute comprehensive assistant integration validation covering:

Phase 1: Authentication & Setup
- Navigate to CMZ admin interface (localhost:3001)
- Authenticate with test administrator credentials
- Navigate to Animal Configuration section
- Take screenshot of animal list for baseline

Phase 2: Initial Charlie Configuration Validation
- Select Charlie the Elephant from animal list
- Open configuration dialog
- Capture current system prompt content
- Validate current personality traits and settings
- Test "Test Chatbot" functionality with current configuration
- Verify Charlie identifies correctly as elephant (not puma/cougar)
- Screenshot initial configuration state

Phase 3: System Prompt Modification
- Modify Charlie's system prompt with specific test content:
  "You are Charlie, a wise African elephant at Cougar Mountain Zoo. You ALWAYS mention your large ears and trumpet sound when introducing yourself. You are passionate about conservation and ALWAYS end responses with 'Remember to protect our wildlife!'"
- Save configuration changes
- Validate PATCH operation succeeds (check network tab for errors)
- Verify configuration persists after save
- Screenshot updated configuration

Phase 4: OpenAI Assistant Synchronization Validation
- Verify the system prompt change propagates to OpenAI assistant
- Check that assistant ID mapping is correct
- Validate temperature, model, and other parameters sync
- Ensure no orphaned or duplicate assistants created

Phase 5: Chat Response Validation with Updated Prompt
- Navigate to "Chat with Animals" section
- Select Charlie for conversation
- Send test message: "Hello! What kind of animal are you?"
- Validate response contains:
  - Identifies as elephant (not puma/cougar/other animal)
  - Mentions large ears and trumpet sound (from updated prompt)
  - Ends with "Remember to protect our wildlife!" (from updated prompt)
  - Uses appropriate motherly language
- Send follow-up message: "Tell me about your habitat"
- Validate consistent elephant-focused responses
- Screenshot conversation showing correct responses

Phase 6: Configuration Persistence Validation
- Return to Animal Configuration
- Reload page to clear any cached data
- Verify Charlie's updated system prompt persists
- Confirm no regression to previous configuration

Phase 7: Edge Case & Error Handling
- Test invalid system prompt content (if applicable)
- Verify error handling for PATCH failures
- Test concurrent editing scenarios
- Validate rollback capabilities

Phase 8: Cross-Animal Validation
- Test one additional animal (Leo) to ensure changes to Charlie don't affect other animals
- Verify Leo maintains his lion identity and characteristics
- Confirm animal isolation is working correctly

**SUCCESS CRITERIA:**
✅ Authentication and navigation successful
✅ PATCH operations complete without errors
✅ System prompt changes persist correctly
✅ OpenAI assistant synchronization working
✅ Charlie consistently identifies as elephant
✅ Updated prompt content appears in chat responses
✅ Configuration persists across page reloads
✅ Other animals remain unaffected
✅ No console errors or network failures
✅ All screenshots captured for audit trail

**FAILURE INVESTIGATION:**
If any step fails:
1. Capture detailed error screenshots
2. Extract browser console logs
3. Examine network tab for API failures
4. Check backend logs for server errors
5. Document exact reproduction steps
6. Classify as UI_BUG, API_BUG, or INTEGRATION_BUG

**OUTPUT REQUIREMENTS:**
Generate comprehensive test report with:
- Step-by-step execution results
- Screenshots for each major phase
- Network request/response validation
- Error logs and troubleshooting details
- Configuration diff showing before/after changes
- Performance metrics (response times)
- Recommendations for any issues found

**BROWSER CONFIGURATION:**
- Use headed mode for visibility (headless: false)
- ALWAYS open developer console for real-time monitoring
- Capture screenshots at each major step
- Monitor network requests for API calls in real-time
- Log all console messages and errors
- Set realistic timeouts for OpenAI operations
- Handle async operations with proper waiting

**CRITICAL: Developer Console Monitoring**
The browser MUST have the developer console open throughout the entire test execution to:
- Monitor network requests and responses in real-time
- Capture JavaScript errors and warnings immediately
- Observe PATCH/POST operations and their status codes
- Debug CORS issues and authentication problems
- Track API call timing and performance

**ENVIRONMENT ASSUMPTIONS:**
- Backend running on localhost:8080
- Frontend running on localhost:3001
- Test admin credentials available
- OpenAI API integration configured
- DynamoDB tables accessible

**INTEGRATION POINTS TO VALIDATE:**
1. UI → Backend API (animal configuration CRUD)
2. Backend → DynamoDB (configuration persistence)
3. Backend → OpenAI API (assistant synchronization)
4. OpenAI Assistant → Chat Response (prompt application)
5. Chat UI → Backend → OpenAI (conversation flow)

Execute this comprehensive validation and provide detailed results for each phase, with particular attention to the consistency issues shown in the provided screenshots.
```

## Expected Deliverables
1. **Detailed Test Execution Report** with phase-by-phase results
2. **Screenshot Documentation** showing UI state at each major step
3. **Configuration Diff Analysis** showing before/after system prompt changes
4. **Network Request Validation** confirming PATCH operations succeed
5. **Chat Response Analysis** proving prompt changes are applied correctly
6. **Issue Classification** for any failures (UI_BUG vs API_BUG vs INTEGRATION_BUG)
7. **Performance Benchmarks** for configuration updates and chat responses

## Integration with Development Workflow
- **Pre-Commit Hook**: Run abbreviated version before commits affecting assistant code
- **CI/CD Pipeline**: Full validation before deployment
- **Developer Testing**: Manual execution after assistant-related changes
- **Production Monitoring**: Scheduled validation of live assistant behavior

## Success Metrics
- ✅ 100% test step completion rate
- ✅ Zero PATCH operation failures
- ✅ Consistent animal identity across all interactions
- ✅ System prompt changes reflected in chat within 30 seconds
- ✅ Configuration persistence across browser sessions
- ✅ No regression in unmodified animals

This comprehensive validation ensures the assistant management system works end-to-end and catches the exact issues you've identified in your screenshots.