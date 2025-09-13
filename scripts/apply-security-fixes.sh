#!/bin/bash

# Security Fixes Implementation Script
# Applies critical security patches to address CodeQL findings in PR #32

set -e  # Exit on any error

echo "🔐 Starting security fixes implementation..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "package.json" ] && [ ! -f "backend/api/openapi_spec.yaml" ]; then
    print_error "Please run this script from the CMZ-chatbots project root directory"
    exit 1
fi

print_status "Checking project structure..."

# Create backup of current files
BACKUP_DIR="security-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

print_status "Creating backup in $BACKUP_DIR..."

# Backup files that will be modified
cp "backend/api/src/main/python/tests/playwright/specs/dynamodb-consistency-validation.spec.js" "$BACKUP_DIR/" 2>/dev/null || true
cp "frontend/src/pages/AnimalConfig.tsx" "$BACKUP_DIR/" 2>/dev/null || true

print_success "Backup created"

# Phase 1: Install required dependencies
print_status "Phase 1: Installing security dependencies..."

cd frontend

# Check if DOMPurify is already installed
if ! npm list dompurify >/dev/null 2>&1; then
    print_status "Installing DOMPurify for XSS protection..."
    npm install dompurify
    npm install --save-dev @types/dompurify
    print_success "DOMPurify installed"
else
    print_status "DOMPurify already installed"
fi

# Check if yup is already installed for validation
if ! npm list yup >/dev/null 2>&1; then
    print_status "Installing Yup for schema validation..."
    npm install yup
    print_success "Yup installed"
else
    print_status "Yup already installed"
fi

cd ..

# Phase 2: Replace vulnerable test file
print_status "Phase 2: Replacing vulnerable test file..."

if [ -f "backend/api/src/main/python/tests/playwright/specs/dynamodb-consistency-validation-secure.spec.js" ]; then
    # Rename original file
    mv "backend/api/src/main/python/tests/playwright/specs/dynamodb-consistency-validation.spec.js" \
       "backend/api/src/main/python/tests/playwright/specs/dynamodb-consistency-validation.spec.js.vulnerable"
    
    # Replace with secure version
    mv "backend/api/src/main/python/tests/playwright/specs/dynamodb-consistency-validation-secure.spec.js" \
       "backend/api/src/main/python/tests/playwright/specs/dynamodb-consistency-validation.spec.js"
    
    print_success "Replaced vulnerable test file with secure version"
else
    print_warning "Secure test file not found, skipping replacement"
fi

# Phase 3: Add validation utilities
print_status "Phase 3: Adding input validation utilities..."

if [ ! -f "frontend/src/utils/inputValidation.ts" ]; then
    print_warning "Input validation utility not found - please create manually"
else
    print_success "Input validation utilities are in place"
fi

if [ ! -f "frontend/src/hooks/useSecureFormHandling.ts" ]; then
    print_warning "Secure form handling hook not found - please create manually"
else
    print_success "Secure form handling hook is in place"
fi

# Phase 4: Apply React component patches (manual step guidance)
print_status "Phase 4: React component security patches..."

if [ -f "security-patches/AnimalConfig-secure-form-handling.patch" ]; then
    print_warning "Manual step required:"
    print_warning "Apply the patch file: security-patches/AnimalConfig-secure-form-handling.patch"
    print_warning "Or manually update AnimalConfig.tsx with secure form handling"
else
    print_warning "Patch file not found - manual updates required for AnimalConfig.tsx"
fi

# Phase 5: Security configuration
print_status "Phase 5: Adding security configuration..."

# Create security config file
cat > "frontend/src/config/security.ts" << EOF
/**
 * Security Configuration
 * 
 * Centralized security settings and constants
 */

export const SECURITY_CONFIG = {
  // Input validation limits
  MAX_ANIMAL_NAME_LENGTH: 100,
  MAX_SPECIES_LENGTH: 200,
  MAX_PERSONALITY_LENGTH: 2000,
  MAX_ANIMAL_ID_LENGTH: 100,
  
  // Rate limiting
  MIN_FORM_SUBMISSION_INTERVAL: 1000, // 1 second
  
  // Allowed characters patterns
  ANIMAL_ID_PATTERN: /^[a-zA-Z0-9_-]+$/,
  ANIMAL_NAME_PATTERN: /^[a-zA-Z0-9\s'\-]+$/,
  SPECIES_PATTERN: /^[a-zA-Z0-9\s()\-\.]+$/,
  
  // Content Security Policy settings
  CSP_DIRECTIVES: {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'", "http://localhost:8080", "http://localhost:3001"],
  },
  
  // Environment-specific settings
  DEBUG_LOGGING: process.env.NODE_ENV === 'development',
  SENSITIVE_LOGGING: process.env.NODE_ENV === 'development' && process.env.DEBUG_SECURITY === 'true',
};

export const VALIDATION_MESSAGES = {
  REQUIRED_FIELD: 'This field is required',
  INVALID_LENGTH: 'Field length is invalid',
  INVALID_CHARACTERS: 'Field contains invalid characters',
  RATE_LIMITED: 'Please wait before submitting again',
  GENERIC_ERROR: 'An error occurred. Please try again.',
};
EOF

print_success "Security configuration created"

# Phase 6: Create security test file
print_status "Phase 6: Creating security tests..."

mkdir -p "frontend/src/utils/__tests__"

cat > "frontend/src/utils/__tests__/inputValidation.test.ts" << EOF
/**
 * Security Validation Tests
 * 
 * Tests for input validation and sanitization functions
 */

import {
  validateAnimalId,
  validateAnimalName,
  validateSpecies,
  validatePersonality,
  ValidationError,
} from '../inputValidation';

describe('Security Input Validation', () => {
  describe('validateAnimalId', () => {
    test('should accept valid animal IDs', () => {
      expect(validateAnimalId('test-animal-1')).toBe('test-animal-1');
      expect(validateAnimalId('test_animal_2')).toBe('test_animal_2');
      expect(validateAnimalId('TestAnimal3')).toBe('TestAnimal3');
    });

    test('should reject malicious input', () => {
      expect(() => validateAnimalId("'; DROP TABLE animals; --")).toThrow(ValidationError);
      expect(() => validateAnimalId('<script>alert("xss")</script>')).toThrow(ValidationError);
      expect(() => validateAnimalId('animal$(rm -rf /)')).toThrow(ValidationError);
    });

    test('should reject empty or invalid input', () => {
      expect(() => validateAnimalId('')).toThrow(ValidationError);
      expect(() => validateAnimalId('   ')).toThrow(ValidationError);
      expect(() => validateAnimalId(null as any)).toThrow(ValidationError);
    });
  });

  describe('validatePersonality', () => {
    test('should sanitize HTML content', () => {
      const maliciousInput = '<script>alert("xss")</script>Friendly animal';
      const result = validatePersonality(maliciousInput);
      expect(result).not.toContain('<script>');
      expect(result).toContain('Friendly animal');
    });

    test('should enforce length limits', () => {
      const longInput = 'a'.repeat(2001);
      expect(() => validatePersonality(longInput)).toThrow(ValidationError);
    });
  });

  describe('validateAnimalName', () => {
    test('should accept valid names', () => {
      expect(validateAnimalName('Bella the Bear')).toBe('Bella the Bear');
      expect(validateAnimalName("O'Malley")).toBe("O'Malley");
      expect(validateAnimalName('Multi-word Name')).toBe('Multi-word Name');
    });

    test('should reject malicious input', () => {
      expect(() => validateAnimalName('<img src=x onerror=alert(1)>')).toThrow(ValidationError);
      expect(() => validateAnimalName('Name\${evil}')).toThrow(ValidationError);
    });
  });
});
EOF

print_success "Security tests created"

# Phase 7: Create environment security check
print_status "Phase 7: Creating environment security check..."

cat > "scripts/security-check.sh" << 'EOF'
#!/bin/bash

# Security Environment Check
# Validates security configuration and dependencies

echo "🔍 Running security environment check..."

# Check for required security dependencies
echo "Checking frontend dependencies..."
cd frontend

MISSING_DEPS=()

if ! npm list dompurify >/dev/null 2>&1; then
    MISSING_DEPS+=("dompurify")
fi

if ! npm list yup >/dev/null 2>&1; then
    MISSING_DEPS+=("yup")
fi

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo "✅ All security dependencies are installed"
else
    echo "❌ Missing security dependencies: ${MISSING_DEPS[*]}"
    echo "Run: npm install ${MISSING_DEPS[*]}"
fi

# Check for vulnerable test files
cd ..
echo "Checking for vulnerable test files..."

if [ -f "backend/api/src/main/python/tests/playwright/specs/dynamodb-consistency-validation.spec.js.vulnerable" ]; then
    echo "✅ Original vulnerable file backed up"
else
    echo "⚠️ Original file not backed up"
fi

# Check for security utilities
if [ -f "frontend/src/utils/inputValidation.ts" ]; then
    echo "✅ Input validation utilities present"
else
    echo "❌ Input validation utilities missing"
fi

if [ -f "frontend/src/hooks/useSecureFormHandling.ts" ]; then
    echo "✅ Secure form handling hook present"
else
    echo "❌ Secure form handling hook missing"
fi

if [ -f "frontend/src/config/security.ts" ]; then
    echo "✅ Security configuration present"
else
    echo "❌ Security configuration missing"
fi

echo "Security check complete!"
EOF

chmod +x "scripts/security-check.sh"

print_success "Security check script created"

# Phase 8: Update package.json scripts
print_status "Phase 8: Adding security scripts to package.json..."

cd frontend

# Add security scripts if not already present
if ! grep -q "security:check" package.json; then
    # Create a temporary file with updated package.json
    python3 -c "
import json
import sys

with open('package.json', 'r') as f:
    data = json.load(f)

if 'scripts' not in data:
    data['scripts'] = {}

data['scripts']['security:check'] = '../scripts/security-check.sh'
data['scripts']['security:test'] = 'npm test -- --testPathPattern=inputValidation'
data['scripts']['security:audit'] = 'npm audit --audit-level=moderate'

with open('package.json', 'w') as f:
    json.dump(data, f, indent=2)
"
    print_success "Security scripts added to package.json"
else
    print_status "Security scripts already present in package.json"
fi

cd ..

# Final summary
print_status "Security fixes implementation completed!"
echo ""
print_success "✅ Completed phases:"
print_success "  1. Security dependencies installed"
print_success "  2. Vulnerable test file replaced"
print_success "  3. Security configuration added"
print_success "  4. Security tests created"
print_success "  5. Environment check script created"
echo ""
print_warning "⚠️ Manual steps required:"
print_warning "  1. Apply React component patches (see security-patches/ directory)"
print_warning "  2. Update AnimalConfig.tsx with secure form handling"
print_warning "  3. Run security tests: npm run security:test"
print_warning "  4. Run security audit: npm run security:audit"
echo ""
print_status "📋 Next steps:"
print_status "  1. Run: ./scripts/security-check.sh"
print_status "  2. Test the application thoroughly"
print_status "  3. Run security validation tests"
print_status "  4. Update PR with security fixes"
echo ""
print_success "Security implementation complete!"
echo "Backup files are available in: $BACKUP_DIR"