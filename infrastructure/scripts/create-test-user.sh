#!/bin/bash

# Create test user in Cognito User Pool
# This script creates a test user with admin privileges for local testing

set -e

# Configuration
STACK_NAME="cmz-chatbot-cognito"
REGION="${AWS_REGION:-us-west-2}"
TEST_EMAIL="${TEST_EMAIL:-test@cmzoo.org}"
TEST_PASSWORD="${TEST_PASSWORD:-TestPass123!}"
TEST_NAME="${TEST_NAME:-Test User}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}👤 Creating test user in Cognito...${NC}"
echo "📋 Configuration:"
echo "  Email: $TEST_EMAIL"
echo "  Name: $TEST_NAME"
echo "  Region: $REGION"
echo ""

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS CLI not configured or no valid credentials${NC}"
    echo "Please run: aws configure --profile cmz"
    exit 1
fi

# Get User Pool ID from CloudFormation stack
echo -e "${YELLOW}🔍 Getting User Pool ID from CloudFormation stack...${NC}"
USER_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
    --output text \
    --region $REGION 2>/dev/null)

if [ -z "$USER_POOL_ID" ] || [ "$USER_POOL_ID" == "None" ]; then
    echo -e "${RED}❌ Could not get User Pool ID from stack: $STACK_NAME${NC}"
    echo "Make sure the Cognito stack is deployed first with deploy-cognito.sh"
    exit 1
fi

echo -e "${GREEN}✅ User Pool ID: $USER_POOL_ID${NC}"
echo ""

# Check if user already exists
echo -e "${YELLOW}🔍 Checking if user already exists...${NC}"
if aws cognito-idp admin-get-user \
    --user-pool-id "$USER_POOL_ID" \
    --username "$TEST_EMAIL" \
    --region $REGION > /dev/null 2>&1; then
    
    echo -e "${YELLOW}⚠️ User $TEST_EMAIL already exists${NC}"
    echo "Deleting existing user..."
    
    aws cognito-idp admin-delete-user \
        --user-pool-id "$USER_POOL_ID" \
        --username "$TEST_EMAIL" \
        --region $REGION
        
    echo -e "${GREEN}✅ Existing user deleted${NC}"
fi

# Create test user
echo -e "${YELLOW}🏗️ Creating test user...${NC}"
aws cognito-idp admin-create-user \
    --user-pool-id "$USER_POOL_ID" \
    --username "$TEST_EMAIL" \
    --user-attributes \
        Name=email,Value="$TEST_EMAIL" \
        Name=name,Value="$TEST_NAME" \
        Name=email_verified,Value=true \
    --temporary-password "$TEST_PASSWORD" \
    --message-action SUPPRESS \
    --region $REGION

echo -e "${GREEN}✅ Test user created${NC}"

# Set permanent password
echo -e "${YELLOW}🔐 Setting permanent password...${NC}"
aws cognito-idp admin-set-user-password \
    --user-pool-id "$USER_POOL_ID" \
    --username "$TEST_EMAIL" \
    --password "$TEST_PASSWORD" \
    --permanent \
    --region $REGION

echo -e "${GREEN}✅ Password set to permanent${NC}"

# Add user to admin group
echo -e "${YELLOW}👥 Adding user to admin group...${NC}"
aws cognito-idp admin-add-user-to-group \
    --user-pool-id "$USER_POOL_ID" \
    --username "$TEST_EMAIL" \
    --group-name "admin" \
    --region $REGION

echo -e "${GREEN}✅ User added to admin group${NC}"
echo ""

echo -e "${GREEN}🎉 Test user creation complete!${NC}"
echo ""
echo -e "${YELLOW}Test User Credentials:${NC}"
echo "  Email: $TEST_EMAIL"
echo "  Password: $TEST_PASSWORD"
echo "  Role: admin"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test login with these credentials"
echo "2. Verify role-based access control"
echo "3. Test token validation and refresh"