#!/bin/bash

# ===========================================
# CMZ Chatbots Environment Setup Script
# For fresh Ubuntu installations
# ===========================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
INSTALL_DIR="$HOME/projects"
PROJECT_NAME="CMZ-chatbots"
CREDENTIALS_FILE=""
SKIP_SYSTEM_PACKAGES=false
SKIP_CLONE=false

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 -c <credentials-file> [OPTIONS]

Required:
  -c <file>    Path to filled credentials file (from credentials-template.env)

Options:
  -d <dir>     Installation directory (default: $HOME/projects)
  -s           Skip system package installation
  -g           Skip git clone (assume repo exists)
  -h           Show this help message

Example:
  $0 -c ~/cmz-credentials.env
  $0 -c ~/cmz-credentials.env -d /opt/projects -s

EOF
    exit 1
}

# Parse command line arguments
while getopts "c:d:sgh" opt; do
    case $opt in
        c)
            CREDENTIALS_FILE="$OPTARG"
            ;;
        d)
            INSTALL_DIR="$OPTARG"
            ;;
        s)
            SKIP_SYSTEM_PACKAGES=true
            ;;
        g)
            SKIP_CLONE=true
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
    esac
done

# Check if credentials file is provided
if [ -z "$CREDENTIALS_FILE" ]; then
    print_error "Credentials file is required!"
    usage
fi

# Check if credentials file exists
if [ ! -f "$CREDENTIALS_FILE" ]; then
    print_error "Credentials file not found: $CREDENTIALS_FILE"
    exit 1
fi

# Validate credentials file
if grep -q "<REPLACE_ME>" "$CREDENTIALS_FILE"; then
    print_error "Credentials file contains unset values (<REPLACE_ME>). Please fill in all required values."
    exit 1
fi

# Load credentials
source "$CREDENTIALS_FILE"

print_status "Starting CMZ Chatbots environment setup..."
print_status "Installation directory: $INSTALL_DIR"
print_status "Project: $PROJECT_NAME"

# Create installation directory
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Step 1: Install system packages (if not skipped)
if [ "$SKIP_SYSTEM_PACKAGES" = false ]; then
    print_status "Installing system packages..."

    # Update package list
    sudo apt-get update

    # Install essential packages
    sudo apt-get install -y \
        curl \
        wget \
        git \
        make \
        jq \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release

    # Install Python 3.11
    print_status "Installing Python 3.11..."
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update
    sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

    # Install Node.js 18
    print_status "Installing Node.js 18..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -  # nosemgrep: bash.curl.security.curl-pipe-bash
    sudo apt-get install -y nodejs

    # Install Docker
    print_status "Installing Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Add current user to docker group
    sudo usermod -aG docker $USER
    print_warning "You'll need to log out and back in for docker group changes to take effect"

    # Install AWS CLI v2
    print_status "Installing AWS CLI v2..."
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "/tmp/awscliv2.zip"
    cd /tmp
    unzip -q awscliv2.zip
    sudo ./aws/install
    cd -
    rm -rf /tmp/awscliv2.zip /tmp/aws

    # Install GitHub CLI
    print_status "Installing GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt-get update
    sudo apt-get install -y gh

    # Install UV (Python package manager)
    print_status "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

else
    print_warning "Skipping system package installation"
fi

# Step 2: Clone repository (if not skipped)
if [ "$SKIP_CLONE" = false ]; then
    print_status "Cloning CMZ repository..."
    if [ -d "$PROJECT_NAME" ]; then
        print_warning "Project directory already exists, pulling latest..."
        cd "$PROJECT_NAME"
        git pull origin dev
    else
        git clone https://github.com/nortal/CMZ-chatbots.git "$PROJECT_NAME"
        cd "$PROJECT_NAME"
        git checkout dev
    fi
else
    print_warning "Skipping repository clone"
    cd "$PROJECT_NAME"
fi

PROJECT_DIR="$INSTALL_DIR/$PROJECT_NAME"

# Step 3: Configure AWS
print_status "Configuring AWS CLI..."
mkdir -p ~/.aws

cat > ~/.aws/config << EOF
[default]
region = ${AWS_REGION}
output = json

[profile ${AWS_PROFILE}]
region = ${AWS_REGION}
output = json
EOF

cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}

[${AWS_PROFILE}]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOF

chmod 600 ~/.aws/credentials

# Step 4: Configure Git
print_status "Configuring Git..."
git config --global user.name "${GITHUB_USERNAME}"
git config --global user.email "${GITHUB_EMAIL}"

# Step 5: Configure GitHub CLI
print_status "Configuring GitHub CLI..."
echo "${GITHUB_TOKEN}" | gh auth login --with-token

# Step 6: Create .env.local file
print_status "Creating .env.local file..."
cat > "$PROJECT_DIR/.env.local" << EOF
# Auto-generated by setup-cmz-environment.sh
# Generated: $(date)

# AWS Configuration
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}"
export AWS_REGION="${AWS_REGION}"
export AWS_PROFILE="${AWS_PROFILE}"

# Jira Configuration
export JIRA_API_TOKEN="${JIRA_API_TOKEN}"
export JIRA_EMAIL="${JIRA_EMAIL}"
export JIRA_BASE_URL="${JIRA_BASE_URL}"

# GitHub Configuration
export GITHUB_TOKEN="${GITHUB_TOKEN}"
export GITHUB_USERNAME="${GITHUB_USERNAME}"
export GITHUB_EMAIL="${GITHUB_EMAIL}"

# DynamoDB Tables
export FAMILY_DYNAMO_TABLE_NAME="${FAMILY_DYNAMO_TABLE_NAME}"
export FAMILY_DYNAMO_PK_NAME="${FAMILY_DYNAMO_PK_NAME}"
export ANIMAL_DYNAMO_TABLE_NAME="${ANIMAL_DYNAMO_TABLE_NAME}"
export ANIMAL_DYNAMO_PK_NAME="${ANIMAL_DYNAMO_PK_NAME}"
export USER_DYNAMO_TABLE_NAME="${USER_DYNAMO_TABLE_NAME}"
export USER_DYNAMO_PK_NAME="${USER_DYNAMO_PK_NAME}"
export CONVERSATION_DYNAMO_TABLE_NAME="${CONVERSATION_DYNAMO_TABLE_NAME}"
export CONVERSATION_DYNAMO_PK_NAME="${CONVERSATION_DYNAMO_PK_NAME}"
export KNOWLEDGE_DYNAMO_TABLE_NAME="${KNOWLEDGE_DYNAMO_TABLE_NAME}"
export KNOWLEDGE_DYNAMO_PK_NAME="${KNOWLEDGE_DYNAMO_PK_NAME}"
export MEDIA_DYNAMO_TABLE_NAME="${MEDIA_DYNAMO_TABLE_NAME}"
export MEDIA_DYNAMO_PK_NAME="${MEDIA_DYNAMO_PK_NAME}"

# Application Configuration
export JWT_SECRET_KEY="${JWT_SECRET_KEY}"
export API_PORT="${API_PORT}"
export FRONTEND_PORT="${FRONTEND_PORT}"
export FRONTEND_URL="${FRONTEND_URL}"
export API_URL="${API_URL}"

# Docker Configuration
export DOCKER_BUILDKIT="${DOCKER_BUILDKIT}"
export COMPOSE_DOCKER_CLI_BUILD="${COMPOSE_DOCKER_CLI_BUILD}"

# Python Configuration
export PYTHONPATH="${PYTHONPATH}"

# Node Configuration
export NODE_ENV="${NODE_ENV}"
export NODE_OPTIONS="${NODE_OPTIONS}"

# Project Configuration
export PROJECT_NAME="${PROJECT_NAME}"
export PROJECT_KEY="${PROJECT_KEY}"
export JIRA_PROJECT_KEY="${JIRA_PROJECT_KEY}"
export JIRA_EPIC_KEY="${JIRA_EPIC_KEY}"

# Optional Services
$([ ! -z "$CLICKSEND_USERNAME" ] && echo "export CLICKSEND_USERNAME=\"${CLICKSEND_USERNAME}\"")
$([ ! -z "$CLICKSEND_API_KEY" ] && echo "export CLICKSEND_API_KEY=\"${CLICKSEND_API_KEY}\"")
$([ ! -z "$OPENAI_API_KEY" ] && echo "export OPENAI_API_KEY=\"${OPENAI_API_KEY}\"")
$([ ! -z "$ANTHROPIC_API_KEY" ] && echo "export ANTHROPIC_API_KEY=\"${ANTHROPIC_API_KEY}\"")
$([ ! -z "$TEAMS_WEBHOOK_URL" ] && echo "export TEAMS_WEBHOOK_URL=\"${TEAMS_WEBHOOK_URL}\"")
EOF

# Step 7: Create shell profile additions
print_status "Adding environment to shell profile..."

SHELL_RC=""
if [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

if [ ! -z "$SHELL_RC" ]; then
    # Remove old CMZ environment setup if exists
    sed -i '/# CMZ Chatbots Environment/,/# End CMZ Environment/d' "$SHELL_RC"

    # Add new environment setup
    cat >> "$SHELL_RC" << EOF

# CMZ Chatbots Environment
export CMZ_PROJECT_DIR="$PROJECT_DIR"
if [ -f "\$CMZ_PROJECT_DIR/.env.local" ]; then
    source "\$CMZ_PROJECT_DIR/.env.local"
fi
alias cmz='cd \$CMZ_PROJECT_DIR'
alias cmz-api='cd \$CMZ_PROJECT_DIR && make run-api'
alias cmz-frontend='cd \$CMZ_PROJECT_DIR/frontend && npm run dev'
alias cmz-test='cd \$CMZ_PROJECT_DIR && python -m pytest tests/integration/test_api_validation_epic.py -v'
alias cmz-nextfive='cd \$CMZ_PROJECT_DIR && source .env.local && echo "Ready for /nextfive workflow"'
# End CMZ Environment
EOF
    print_status "Shell aliases added to $SHELL_RC"
fi

# Step 8: Install Python dependencies
print_status "Installing Python dependencies..."
cd "$PROJECT_DIR/backend/api"

# Create virtual environment
python3.11 -m venv .venv/openapi-venv

# Activate and install dependencies
source .venv/openapi-venv/bin/activate
pip install --upgrade pip
pip install -r src/main/python/requirements.txt
deactivate

# Step 9: Install Node dependencies
print_status "Installing Node dependencies..."
cd "$PROJECT_DIR/frontend"
npm install

# Step 10: Build Docker images
print_status "Building Docker images..."
cd "$PROJECT_DIR"
make build-api || print_warning "Docker build failed - may need to restart for docker group changes"

# Step 11: Validate setup
print_status "Validating environment setup..."

echo ""
echo "==================================="
echo "VALIDATION RESULTS:"
echo "==================================="

# Check AWS
if aws sts get-caller-identity --profile ${AWS_PROFILE} > /dev/null 2>&1; then
    print_status "AWS credentials valid"
else
    print_error "AWS credentials invalid"
fi

# Check Jira
if curl -s -u "${JIRA_EMAIL}:${JIRA_API_TOKEN}" "${JIRA_BASE_URL}/rest/api/3/myself" | grep -q "emailAddress"; then
    print_status "Jira credentials valid"
else
    print_error "Jira credentials invalid"
fi

# Check GitHub
if gh auth status > /dev/null 2>&1; then
    print_status "GitHub authentication valid"
else
    print_error "GitHub authentication invalid"
fi

# Check Docker
if docker ps > /dev/null 2>&1; then
    print_status "Docker is accessible"
else
    print_warning "Docker not accessible - log out and back in for group changes"
fi

# Check Python environment
if [ -f "$PROJECT_DIR/backend/api/.venv/openapi-venv/bin/python" ]; then
    print_status "Python environment created"
else
    print_error "Python environment not found"
fi

# Check Node modules
if [ -d "$PROJECT_DIR/frontend/node_modules" ]; then
    print_status "Node modules installed"
else
    print_error "Node modules not found"
fi

echo ""
echo "==================================="
echo "SETUP COMPLETE!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Log out and back in for docker group changes to take effect"
echo "2. Source your shell profile: source $SHELL_RC"
echo "3. Navigate to project: cmz"
echo "4. Run API: cmz-api"
echo "5. Run Frontend: cmz-frontend"
echo "6. Test /nextfive: cmz-nextfive"
echo ""
echo "Useful aliases added:"
echo "  cmz         - Navigate to project directory"
echo "  cmz-api     - Start backend API"
echo "  cmz-frontend - Start frontend development server"
echo "  cmz-test    - Run integration tests"
echo "  cmz-nextfive - Prepare for /nextfive workflow"
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Credentials saved: $PROJECT_DIR/.env.local"
echo ""
print_status "Setup script completed successfully!"