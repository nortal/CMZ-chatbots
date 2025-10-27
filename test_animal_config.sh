#!/bin/bash

echo "Testing Animal Config PATCH with numeric temperature and topP..."

# Test with numeric values
curl -X PATCH http://localhost:8080/animal_config/leo_001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock-token" \
  -d '{
    "temperature": 1.5,
    "topP": 0.95,
    "voice": "default",
    "aiModel": "gpt-4",
    "toolsEnabled": true,
    "name": "Leo",
    "species": "Lion",
    "personality": "Confident and regal"
  }' -v

echo -e "\n\nTest complete. Check response for temperature type validation."