#!/usr/bin/env python3
"""
Fix Recurring Post-Generation Issues
Addresses problems that keep reappearing after make generate-api:
1. Missing flask-cors dependency
2. Missing AWS dependencies (boto3, pynamodb)
3. Missing CORS configuration in __main__.py
4. Centralized JWT usage in auth_mock.py
5. Proper email extraction in handlers.py
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

class RecurringIssuesFixer:
    def __init__(self, src_dir: Path):
        self.src_dir = Path(src_dir)
        self.fixes_applied = []
        self.errors = []

    def fix_all(self) -> bool:
        """Apply all recurring fixes"""
        print("🔧 Fixing recurring post-generation issues...")

        success = True
        success &= self.fix_requirements()
        success &= self.fix_main_cors()
        success &= self.fix_auth_mock_jwt()
        success &= self.fix_handlers_email()

        self.report_results()
        return success

    def fix_requirements(self) -> bool:
        """Ensure critical dependencies are in requirements.txt"""
        print("📦 Fixing requirements.txt...")

        req_file = self.src_dir / "requirements.txt"
        if not req_file.exists():
            self.errors.append(f"Requirements file not found: {req_file}")
            return False

        content = req_file.read_text()
        original_content = content

        # Check for flask-cors
        if not re.search(r'flask-cors\s*>=?\s*\d', content, re.IGNORECASE):
            # Find Flask line and add flask-cors after it
            if 'Flask ==' in content:
                content = content.replace(
                    'Flask == 2.1.1',
                    'Flask == 2.1.1\nflask-cors >= 3.0.10'
                )
                self.fixes_applied.append("Added flask-cors >= 3.0.10 to requirements.txt")
            else:
                # Add at end of main dependencies
                lines = content.split('\n')
                insert_idx = next((i for i, line in enumerate(lines) if line.strip() == ''), len(lines))
                lines.insert(insert_idx, 'flask-cors >= 3.0.10')
                content = '\n'.join(lines)
                self.fixes_applied.append("Added flask-cors to requirements.txt")

        # Check for AWS dependencies
        if not re.search(r'boto3\s*>=?\s*\d', content):
            if '\n\n' in content:
                # Add AWS section if not present
                content = content.replace('\n\n', '\n\n# AWS SDK and ORM\nboto3 >= 1.26.0\npynamodb >= 5.5.0\n\n', 1)
                self.fixes_applied.append("Added AWS dependencies (boto3, pynamodb)")

        if content != original_content:
            req_file.write_text(content)
            print(f"  ✅ Updated {req_file}")
            return True
        else:
            print(f"  ✓ Requirements already correct")
            return True

    def fix_main_cors(self) -> bool:
        """Ensure CORS is configured in __main__.py"""
        print("🌐 Fixing CORS configuration in __main__.py...")

        main_file = self.src_dir / "openapi_server/__main__.py"
        if not main_file.exists():
            self.errors.append(f"Main file not found: {main_file}")
            return False

        content = main_file.read_text()
        original_content = content

        # Check if CORS import exists
        has_cors_import = 'from flask_cors import CORS' in content
        has_cors_config = 'CORS(app.app' in content

        if not has_cors_import:
            # Add import after connexion import
            content = content.replace(
                'import connexion',
                'import connexion\nfrom flask_cors import CORS'
            )
            self.fixes_applied.append("Added flask_cors import to __main__.py")

        if not has_cors_config:
            # Add CORS configuration after app setup
            cors_config = '''
    # Enable CORS for all routes to allow frontend access
    CORS(app.app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://localhost:3001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
'''
            # Find the line with add_api and insert CORS before it
            if 'app.add_api' in content:
                lines = content.split('\n')
                insert_idx = next(i for i, line in enumerate(lines) if 'app.add_api' in line)
                lines.insert(insert_idx, cors_config)
                content = '\n'.join(lines)
                self.fixes_applied.append("Added CORS configuration to __main__.py")

        if content != original_content:
            main_file.write_text(content)
            print(f"  ✅ Updated {main_file}")
            return True
        else:
            print(f"  ✓ CORS configuration already correct")
            return True

    def fix_auth_mock_jwt(self) -> bool:
        """Ensure auth_mock.py uses centralized JWT generation"""
        print("🔐 Fixing auth_mock.py JWT generation...")

        auth_mock_file = self.src_dir / "openapi_server/impl/auth_mock.py"
        if not auth_mock_file.exists():
            print(f"  ℹ️  auth_mock.py not found (may not be using mock auth)")
            return True

        content = auth_mock_file.read_text()
        original_content = content

        # Check if it's using centralized JWT utils
        if 'from .utils.jwt_utils import generate_jwt_token' not in content:
            # Replace the generate_mock_token function
            pattern = r'def generate_mock_token\([^)]*\):[^}]*?(?=\n(?:def |class |$))'

            replacement = '''def generate_mock_token(email: str, role: str) -> str:
    """
    Generate a JWT token using centralized jwt_utils.
    This ensures frontend compatibility by including all required fields:
    - user_id, userId (both formats for compatibility)
    - email, role
    - user_type (some frontend code uses this)
    - exp, iat, iss, sub (standard JWT claims)
    """
    user_data = {
        'email': email,
        'role': role,
        # Generate user_id from email if not provided
        'user_id': email.replace('@', '_').replace('.', '_')
    }

    # Use centralized JWT generation to ensure frontend compatibility
    return generate_jwt_token(user_data, expiration_seconds=86400)  # 24 hours
'''

            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)

                # Add import if not present
                if 'from .utils.jwt_utils import generate_jwt_token' not in content:
                    # Add after other imports
                    import_pattern = r'(from datetime import[^\n]*\n)'
                    if re.search(import_pattern, content):
                        content = re.sub(
                            import_pattern,
                            r'\1from .utils.jwt_utils import generate_jwt_token\n',
                            content
                        )
                    else:
                        # Add at top after docstring
                        content = content.replace(
                            '"""',
                            '"""\n\nfrom .utils.jwt_utils import generate_jwt_token',
                            1
                        ).replace('"""', '"""', 1)

                self.fixes_applied.append("Updated auth_mock.py to use centralized JWT generation")

        if content != original_content:
            auth_mock_file.write_text(content)
            print(f"  ✅ Updated {auth_mock_file}")
            return True
        else:
            print(f"  ✓ JWT generation already using centralized utils")
            return True

    def fix_handlers_email(self) -> bool:
        """Ensure handlers.py properly extracts email from request body"""
        print("📧 Fixing email extraction in handlers.py...")

        handlers_file = self.src_dir / "openapi_server/impl/handlers.py"
        if not handlers_file.exists():
            print(f"  ℹ️  handlers.py not found")
            return True

        content = handlers_file.read_text()
        original_content = content

        # Fix email extraction pattern in handle_login_post
        # OLD: email = body.get('username', body.get('email', ''))
        # NEW: email = body.get('username') or body.get('email', '')
        old_pattern = r"email\s*=\s*body\.get\('username',\s*body\.get\('email',\s*''\)\)"
        new_pattern = "email = body.get('username') or body.get('email', '')"

        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_pattern, content)
            self.fixes_applied.append("Fixed email extraction to handle null username in handlers.py")

        if content != original_content:
            handlers_file.write_text(content)
            print(f"  ✅ Updated {handlers_file}")
            return True
        else:
            print(f"  ✓ Email extraction already correct")
            return True

    def report_results(self):
        """Report all fixes applied and any errors"""
        print("\n" + "="*60)
        if self.fixes_applied:
            print("✅ Fixes Applied:")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
        else:
            print("✓ No fixes needed - all configurations already correct")

        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  • {error}")
            return False

        print("="*60)
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_recurring_issues.py <src_directory>")
        print("Example: fix_recurring_issues.py backend/api/src/main/python")
        sys.exit(1)

    src_dir = Path(sys.argv[1])
    if not src_dir.exists():
        print(f"ERROR: Source directory not found: {src_dir}")
        sys.exit(1)

    fixer = RecurringIssuesFixer(src_dir)
    success = fixer.fix_all()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
