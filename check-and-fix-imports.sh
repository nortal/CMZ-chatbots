#!/bin/bash
echo "🔍 Checking OpenAPI Generation..."

# Check auth imports
if grep -q "from openapi_server.models.auth_response import AuthResponse" \
    backend/api/src/main/python/openapi_server/controllers/auth_controller.py; then
    echo "✅ Auth controller has AuthResponse import"
else
    echo "❌ Auth controller missing AuthResponse - FIXING..."
    sed -i '' '/from openapi_server.models.auth_request import AuthRequest/a\
from openapi_server.models.auth_response import AuthResponse\
from openapi_server.models.password_reset_request import PasswordResetRequest' \
    backend/api/src/main/python/openapi_server/controllers/auth_controller.py
fi

# Check animals imports  
if grep -q "from openapi_server.models.animal_config_update import AnimalConfigUpdate" \
    backend/api/src/main/python/openapi_server/controllers/animals_controller.py; then
    echo "✅ Animals controller has AnimalConfigUpdate import"
else
    echo "❌ Animals controller missing AnimalConfigUpdate - FIXING..."
    sed -i '' '6i\
from openapi_server.models.animal_config_update import AnimalConfigUpdate' \
    backend/api/src/main/python/openapi_server/controllers/animals_controller.py
fi

echo "🏁 Check complete!"
