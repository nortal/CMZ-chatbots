# Pre-Test Setup Advice

**CRITICAL**: Always verify frontend and backend are running properly before executing any validation tests.

## Quick Health Check Commands

### 1. Verify Frontend Status
```bash
# Check if frontend is running on common ports
curl -f http://localhost:3000 || echo "Frontend not on port 3000"
curl -f http://localhost:3001 || echo "Frontend not on port 3001"

# Alternative: Check for React/Vite development server
lsof -i :3000 -i :3001 | grep LISTEN
```

### 2. Verify Backend API Status
```bash
# Check if backend API is running
curl -f http://localhost:8080/health || echo "Backend API not responding"
curl -f http://localhost:8080/api/health || echo "Try /api/health endpoint"

# Alternative: Check for Flask/Python server
lsof -i :8080 | grep LISTEN
```

### 3. Quick Database Connectivity
```bash
# Verify AWS profile and DynamoDB access
aws sts get-caller-identity --profile cmz
aws dynamodb list-tables --region us-west-2 --profile cmz | head -10
```

## Complete System Startup

### Frontend Startup (Choose Method)
```bash
# Method 1: From frontend directory
cd frontend && npm run dev

# Method 2: From project root (if configured)
make run-frontend

# Method 3: Check package.json for specific commands
cd frontend && cat package.json | grep -A5 '"scripts"'
```

### Backend API Startup
```bash
# Standard Docker approach (recommended)
make generate-api && make build-api && make run-api

# Alternative: Local Python approach
cd backend/api/src/main/python
source .venv/openapi-venv/bin/activate
python -m openapi_server

# Verify with health check
curl http://localhost:8080/health
```

### Container-Based Verification
```bash
# Check running containers
docker ps | grep -E "(frontend|backend|cmz)"

# Check container logs
docker logs cmz-api-container
docker logs frontend-container
```

## Environment Validation

### Required Environment Variables
```bash
# AWS Configuration (check these exist)
echo "AWS_PROFILE: $AWS_PROFILE"          # Should be: cmz
echo "AWS_REGION: $AWS_REGION"            # Should be: us-west-2
echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"  # Should be set
echo "AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY" # Should be set

# Application Configuration
echo "PORT: $PORT"                        # Backend port (default 8080)
echo "FRONTEND_URL: $FRONTEND_URL"        # Frontend URL for tests
```

### DynamoDB Table Verification
```bash
# Verify all required tables exist
aws dynamodb list-tables --region us-west-2 --profile cmz --output table

# Expected tables:
# - quest-dev-animal
# - quest-dev-animal-config
# - quest-dev-family
# - quest-dev-user
# - quest-dev-conversation
# - quest-dev-knowledge
# - quest-dev-session
```

## Common Startup Issues

### Port Conflicts
```bash
# Kill processes on common ports
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

# Alternative: Find and kill by process name
pkill -f "node.*vite\|webpack-dev-server"
pkill -f "python.*openapi_server"
```

### Docker Issues
```bash
# Clean up stale containers
docker stop cmz-api-container 2>/dev/null
docker rm cmz-api-container 2>/dev/null

# Clean up Docker resources
docker system prune -f

# Rebuild from scratch if needed
make clean-api && make generate-api && make build-api && make run-api
```

### Dependency Issues
```bash
# Frontend dependency refresh
cd frontend && npm install

# Backend dependency refresh
cd backend/api/src/main/python && pip install -r requirements.txt
```

## Pre-Test Verification Checklist

### ✅ System Status
- [ ] Frontend accessible (http://localhost:3000 or 3001)
- [ ] Backend API responding (http://localhost:8080/health)
- [ ] AWS credentials configured (aws sts get-caller-identity)
- [ ] DynamoDB tables accessible (aws dynamodb list-tables)

### ✅ Authentication Flow
- [ ] Admin login page loads
- [ ] Login with admin/admin123 succeeds
- [ ] Dashboard navigation works
- [ ] No 401/403 errors in browser console

### ✅ Database Connectivity
- [ ] Can query animal tables (aws dynamodb scan --table-name quest-dev-animal)
- [ ] Tables contain expected test data
- [ ] No AWS credential errors

### ✅ Network Configuration
- [ ] No CORS errors in browser console
- [ ] API endpoints returning expected responses
- [ ] No network timeout issues

## Quick Recovery Commands

### Complete System Reset
```bash
# Nuclear option: restart everything
pkill -f "node\|python\|vite"
docker stop $(docker ps -q) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null

# Wait 5 seconds
sleep 5

# Restart backend
make generate-api && make build-api && make run-api

# In new terminal: Restart frontend
cd frontend && npm run dev
```

### Environment Reset
```bash
# Reload AWS credentials
source ~/.zshrc
aws configure list --profile cmz

# Reload environment variables
source .env.local 2>/dev/null || echo "No .env.local found"
```

## Testing-Specific Setup

### Playwright Configuration
```bash
# Ensure Playwright browsers installed
cd backend/api/src/main/python/tests/playwright
npx playwright install

# Set correct frontend URL for tests
export FRONTEND_URL=http://localhost:3000  # or 3001
```

### Test User Setup
```bash
# Verify test users exist in DynamoDB
aws dynamodb get-item --table-name quest-dev-user \
  --key '{"userId":{"S":"admin"}}' \
  --region us-west-2 --profile cmz
```

## Troubleshooting Commands

### Debug Frontend Issues
```bash
# Check frontend build/dev server logs
cd frontend && npm run dev 2>&1 | tee frontend.log

# Check for JavaScript errors
curl -s http://localhost:3000 | grep -i error
```

### Debug Backend Issues
```bash
# Check API server logs
make logs-api

# Test specific API endpoints
curl -v http://localhost:8080/animals
curl -v http://localhost:8080/health
```

### Debug Authentication Issues
```bash
# Test login endpoint directly
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## Success Indicators

### ✅ Ready for Testing
- Frontend loads without console errors
- Backend API health check returns 200 OK
- Admin login works and redirects to dashboard
- No 401/403 authentication errors
- DynamoDB queries return expected data
- All required ports accessible (3000/3001, 8080)

### ❌ Not Ready for Testing
- Connection refused errors on frontend/backend ports
- 500/401/403 errors in browser console
- AWS credential or DynamoDB access errors
- Docker containers failing to start
- Missing environment variables

## Final Pre-Test Command
```bash
# One-liner to verify everything is working
curl -f http://localhost:3000 && \
curl -f http://localhost:8080/health && \
aws dynamodb list-tables --region us-west-2 --profile cmz >/dev/null && \
echo "✅ System ready for testing" || \
echo "❌ System not ready - check components above"
```

**Remember**: Always run this verification before executing `/validate-animal-config`, `/report-bugs`, `/nextfive`, or any other validation commands.