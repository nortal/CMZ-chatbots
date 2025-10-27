#!/bin/bash
echo "🔧 Fixing common CMZ development issues..."

cd "$(dirname "$0")/.."

# Fix import paths (common after OpenAPI regeneration)
echo "🔄 Fixing import paths..."
find backend/api/src/main/python/openapi_server/controllers -name "*.py" -exec sed -i '' 's/from openapi_server\.controllers\.impl/from openapi_server.impl/g' {} \;
find backend/api/src/main/python/openapi_server/controllers -name "*.py" -exec sed -i '' 's/from openapi_server\.controllers\.models/from openapi_server.models/g' {} \;
find backend/api/src/main/python/openapi_server -name "__main__.py" -exec sed -i '' 's/from  import encoder/from . import encoder/g' {} \;

# Format code
echo "🎨 Formatting code..."
if command -v black >/dev/null 2>&1; then
    black backend/api/src/main/python/openapi_server/impl/
fi

# Remove unused imports (basic cleanup)
echo "🧹 Cleaning up imports..."
find backend/api/src/main/python/openapi_server/impl -name "*.py" -exec python3 -c "
import re
import sys
with open(sys.argv[1], 'r') as f:
    content = f.read()
# Remove duplicate imports
lines = content.split('\n')
seen_imports = set()
cleaned_lines = []
for line in lines:
    if line.strip().startswith('import ') or line.strip().startswith('from '):
        if line not in seen_imports:
            seen_imports.add(line)
            cleaned_lines.append(line)
    else:
        cleaned_lines.append(line)
with open(sys.argv[1], 'w') as f:
    f.write('\n'.join(cleaned_lines))
" {} \;

echo "✅ Common issues fixed - run quality_gates.sh to validate"