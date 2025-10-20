#!/bin/bash

# Setup AWS Cognito User Pool for CMZ Chatbot Authentication
# This script creates the necessary Cognito resources for local testing

set -e

echo "🚀 Setting up AWS Cognito for CMZ Chatbot Authentication..."

# Configuration
POOL_NAME="cmz-chatbot-dev"
CLIENT_NAME="cmz-chatbot-client"
REGION="us-west-2"

echo "📋 Using configuration:"
echo "  Pool Name: $POOL_NAME"
echo "  Client Name: $CLIENT_NAME"
echo "  Region: $REGION"
echo ""

# Check AWS CLI configuration
echo "🔍 Checking AWS CLI configuration..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured or no valid credentials"
    echo "Please run: aws configure --profile cmz"
    exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS CLI configured for account: $ACCOUNT_ID"
echo ""

# Create Cognito User Pool
echo "🏗️  Creating Cognito User Pool..."
USER_POOL_OUTPUT=$(aws cognito-idp create-user-pool \
    --pool-name "$POOL_NAME" \
    --policies '{
        "PasswordPolicy": {
            "MinimumLength": 8,
            "RequireUppercase": false,
            "RequireLowercase": false,
            "RequireNumbers": false,
            "RequireSymbols": false
        }
    }' \
    --auto-verified-attributes email \
    --username-attributes email \
    --admin-create-user-config '{
        "AllowAdminCreateUserOnly": false,
        "UnusedAccountValidityDays": 7
    }' \
    --verification-message-template '{
        "DefaultEmailOption": "CONFIRM_WITH_CODE",
        "DefaultEmailSubject": "CMZ Chatbot - Verify your account",
        "DefaultEmailMessage": "Your verification code is {####}"
    }' \
    --user-attribute-update-settings '{
        "AttributesRequireVerificationBeforeUpdate": ["email"]
    }' \
    --region $REGION \
    --output json)

USER_POOL_ID=$(echo $USER_POOL_OUTPUT | jq -r '.UserPool.Id')
echo "✅ User Pool created: $USER_POOL_ID"

# Create User Pool Client
echo "🔧 Creating User Pool Client..."
CLIENT_OUTPUT=$(aws cognito-idp create-user-pool-client \
    --user-pool-id "$USER_POOL_ID" \
    --client-name "$CLIENT_NAME" \
    --generate-secret \
    --explicit-auth-flows "USER_PASSWORD_AUTH" "ADMIN_NO_SRP_AUTH" \
    --supported-identity-providers "COGNITO" \
    --read-attributes "email" "name" "email_verified" \
    --write-attributes "email" "name" \
    --refresh-token-validity 30 \
    --access-token-validity 60 \
    --id-token-validity 60 \
    --token-validity-units '{
        "AccessToken": "minutes",
        "IdToken": "minutes",
        "RefreshToken": "days"
    }' \
    --region $REGION \
    --output json)

CLIENT_ID=$(echo $CLIENT_OUTPUT | jq -r '.UserPoolClient.ClientId')
CLIENT_SECRET=$(echo $CLIENT_OUTPUT | jq -r '.UserPoolClient.ClientSecret')
echo "✅ User Pool Client created: $CLIENT_ID"

# Create Identity Pool
echo "🆔 Creating Identity Pool..."
IDENTITY_POOL_OUTPUT=$(aws cognito-identity create-identity-pool \
    --identity-pool-name "$POOL_NAME-identity" \
    --allow-unauthenticated-identities false \
    --cognito-identity-providers "ProviderName=cognito-idp.$REGION.amazonaws.com/$USER_POOL_ID,ClientId=$CLIENT_ID,ServerSideTokenCheck=false" \
    --region $REGION \
    --output json)

IDENTITY_POOL_ID=$(echo $IDENTITY_POOL_OUTPUT | jq -r '.IdentityPoolId')
echo "✅ Identity Pool created: $IDENTITY_POOL_ID"

# Create Cognito Groups for RBAC
echo "👥 Creating Cognito Groups..."
aws cognito-idp create-group \
    --group-name "admin" \
    --user-pool-id "$USER_POOL_ID" \
    --description "Administrators with full access" \
    --precedence 1 \
    --region $REGION

aws cognito-idp create-group \
    --group-name "educator" \
    --user-pool-id "$USER_POOL_ID" \
    --description "Educators with animal and family management access" \
    --precedence 2 \
    --region $REGION

aws cognito-idp create-group \
    --group-name "parent" \
    --user-pool-id "$USER_POOL_ID" \
    --description "Parents with family access" \
    --precedence 3 \
    --region $REGION

aws cognito-idp create-group \
    --group-name "student" \
    --user-pool-id "$USER_POOL_ID" \
    --description "Students with read-only access" \
    --precedence 4 \
    --region $REGION

echo "✅ Groups created: admin, educator, parent, student"

# Generate environment configuration
echo ""
echo "🔐 Environment Configuration:"
echo "================================"
echo "export COGNITO_USER_POOL_ID=\"$USER_POOL_ID\""
echo "export COGNITO_CLIENT_ID=\"$CLIENT_ID\""
echo "export COGNITO_CLIENT_SECRET=\"$CLIENT_SECRET\""
echo "export COGNITO_IDENTITY_POOL_ID=\"$IDENTITY_POOL_ID\""
echo "export AWS_REGION=\"$REGION\""
echo ""

# Save to .env file
ENV_FILE="../.env.cognito"
echo "💾 Saving configuration to $ENV_FILE..."
cat > "$ENV_FILE" << EOF
# AWS Cognito Configuration for CMZ Chatbot
COGNITO_USER_POOL_ID=$USER_POOL_ID
COGNITO_CLIENT_ID=$CLIENT_ID
COGNITO_CLIENT_SECRET=$CLIENT_SECRET
COGNITO_IDENTITY_POOL_ID=$IDENTITY_POOL_ID
AWS_REGION=$REGION
EOF

echo "✅ Configuration saved to $ENV_FILE"
echo ""

# Create test user
echo "👤 Creating test user for local testing..."
TEST_EMAIL="test@cmzoo.org"
TEST_PASSWORD="TestPass123!"

aws cognito-idp admin-create-user \
    --user-pool-id "$USER_POOL_ID" \
    --username "$TEST_EMAIL" \
    --user-attributes "Name=email,Value=$TEST_EMAIL" "Name=name,Value=Test User" "Name=email_verified,Value=true" \
    --temporary-password "$TEST_PASSWORD" \
    --message-action SUPPRESS \
    --region $REGION

# Set permanent password
aws cognito-idp admin-set-user-password \
    --user-pool-id "$USER_POOL_ID" \
    --username "$TEST_EMAIL" \
    --password "$TEST_PASSWORD" \
    --permanent \
    --region $REGION

# Add test user to admin group
aws cognito-idp admin-add-user-to-group \
    --user-pool-id "$USER_POOL_ID" \
    --username "$TEST_EMAIL" \
    --group-name "admin" \
    --region $REGION

echo "✅ Test user created: $TEST_EMAIL / $TEST_PASSWORD (admin role)"
echo ""

echo "🎉 AWS Cognito setup complete!"
echo ""
echo "Next steps:"
echo "1. Source the environment file: source .env.cognito"
echo "2. Run the test script: python3 test_cognito_auth.py"
echo ""
echo "Resources created:"
echo "  - User Pool: $USER_POOL_ID"
echo "  - Client: $CLIENT_ID" 
echo "  - Identity Pool: $IDENTITY_POOL_ID"
echo "  - Groups: admin, educator, parent, student"
echo "  - Test User: $TEST_EMAIL (admin)"