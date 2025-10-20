# Guardrails System Design

## Overview
A flexible, admin-configurable guardrails system for managing AI conversation safety and appropriateness rules.

## 1. Data Model

### DynamoDB Tables

#### Table: `quest-dev-guardrails`
```json
{
  "guardrailId": "gr_family_friendly_001",  // Primary Key
  "name": "Family Friendly Content",
  "type": "ALWAYS" | "NEVER" | "ENCOURAGE" | "DISCOURAGE",
  "rule": "Always use responses that are family friendly",
  "description": "Ensures all content is appropriate for children and families",
  "category": "content_safety" | "educational" | "personality" | "technical",
  "priority": 100,  // Higher = more important
  "isActive": true,
  "isGlobal": false,  // If true, applies to ALL animals by default
  "created": {
    "at": "2025-01-09T10:00:00Z",
    "by": "admin@cmz.org"
  },
  "modified": {
    "at": "2025-01-09T10:00:00Z",
    "by": "admin@cmz.org"
  },
  "keywords": ["family", "children", "appropriate", "safe"],  // For search
  "examples": {
    "good": ["That's a great question! Let me tell you about..."],
    "bad": ["inappropriate content example"]
  }
}
```

#### Updated Animal Config Structure
```json
{
  "animalId": "pokey",
  "name": "Pokey the Porcupine",
  // ... existing fields ...
  "guardrails": {
    "selected": ["gr_family_friendly_001", "gr_educational_focus_002", "gr_no_violence_003"],
    "custom": [
      {
        "type": "ALWAYS",
        "rule": "Always mention that porcupine quills are modified hairs"
      },
      {
        "type": "NEVER",
        "rule": "Never suggest touching or petting porcupines"
      }
    ]
  },
  "systemPromptTemplate": {
    "base": "You are {name} at Cougar Mountain Zoo.",
    "personality": "{personality}",
    "facts": "{facts}",
    "guardrails": "{guardrails}"  // Injected from selected rules
  }
}
```

## 2. API Endpoints

### Guardrails Management
```yaml
/guardrails:
  get:
    summary: List all guardrails
    parameters:
      - name: category
        in: query
        schema:
          type: string
          enum: [content_safety, educational, personality, technical]
      - name: isActive
        in: query
        schema:
          type: boolean
      - name: isGlobal
        in: query
        schema:
          type: boolean
    responses:
      200:
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Guardrail'

  post:
    summary: Create new guardrail
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/GuardrailInput'
    responses:
      201:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Guardrail'

/guardrails/{guardrailId}:
  get:
    summary: Get specific guardrail
    parameters:
      - name: guardrailId
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Guardrail'

  patch:
    summary: Update guardrail
    parameters:
      - name: guardrailId
        in: path
        required: true
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/GuardrailUpdate'
    responses:
      200:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Guardrail'

  delete:
    summary: Delete guardrail (soft delete)
    parameters:
      - name: guardrailId
        in: path
        required: true
        schema:
          type: string
    responses:
      204:
        description: Guardrail deleted

/guardrails/templates:
  get:
    summary: Get pre-built guardrail templates
    responses:
      200:
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/GuardrailTemplate'
```

## 3. Implementation

### Guardrails Handler (`impl/guardrails.py`)
```python
import boto3
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('quest-dev-guardrails')

class GuardrailsManager:
    """Manages guardrail rules for AI conversations"""

    # Pre-built templates
    TEMPLATES = {
        'family_friendly': {
            'name': 'Family Friendly Package',
            'rules': [
                {'type': 'ALWAYS', 'rule': 'Always use language appropriate for all ages'},
                {'type': 'NEVER', 'rule': 'Never discuss violence, weapons, or harmful activities'},
                {'type': 'NEVER', 'rule': 'Never use profanity or inappropriate language'},
                {'type': 'ENCOURAGE', 'rule': 'Encourage curiosity and learning'}
            ]
        },
        'educational_focus': {
            'name': 'Educational Focus Package',
            'rules': [
                {'type': 'ALWAYS', 'rule': 'Always include educational facts when relevant'},
                {'type': 'ENCOURAGE', 'rule': 'Encourage questions about wildlife and conservation'},
                {'type': 'ALWAYS', 'rule': 'Always explain complex concepts in simple terms'},
                {'type': 'DISCOURAGE', 'rule': 'Discourage off-topic conversations'}
            ]
        },
        'safety_first': {
            'name': 'Safety First Package',
            'rules': [
                {'type': 'NEVER', 'rule': 'Never suggest dangerous interactions with animals'},
                {'type': 'ALWAYS', 'rule': 'Always emphasize zoo safety rules'},
                {'type': 'NEVER', 'rule': 'Never encourage feeding or touching animals'},
                {'type': 'ALWAYS', 'rule': 'Always mention proper viewing distances'}
            ]
        }
    }

    @classmethod
    def create_guardrail(cls, guardrail_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new guardrail rule"""
        guardrail_id = f"gr_{uuid.uuid4().hex[:12]}"

        item = {
            'guardrailId': guardrail_id,
            'name': guardrail_data['name'],
            'type': guardrail_data['type'],  # ALWAYS, NEVER, ENCOURAGE, DISCOURAGE
            'rule': guardrail_data['rule'],
            'description': guardrail_data.get('description', ''),
            'category': guardrail_data.get('category', 'content_safety'),
            'priority': guardrail_data.get('priority', 50),
            'isActive': guardrail_data.get('isActive', True),
            'isGlobal': guardrail_data.get('isGlobal', False),
            'keywords': guardrail_data.get('keywords', []),
            'examples': guardrail_data.get('examples', {}),
            'created': {
                'at': datetime.now().isoformat(),
                'by': guardrail_data.get('createdBy', 'system')
            },
            'modified': {
                'at': datetime.now().isoformat(),
                'by': guardrail_data.get('createdBy', 'system')
            }
        }

        table.put_item(Item=item)
        return item

    @classmethod
    def get_guardrails_for_animal(cls, animal_id: str) -> List[str]:
        """Get all guardrails for a specific animal"""
        # Get animal config
        animal_table = dynamodb.Table('quest-dev-animal')
        animal_response = animal_table.get_item(Key={'animalId': animal_id})

        if 'Item' not in animal_response:
            return []

        animal = animal_response['Item']
        guardrail_ids = []

        # Get selected guardrail IDs
        if 'guardrails' in animal and 'selected' in animal['guardrails']:
            guardrail_ids.extend(animal['guardrails']['selected'])

        # Get global guardrails
        global_response = table.scan(
            FilterExpression='isGlobal = :true AND isActive = :active',
            ExpressionAttributeValues={':true': True, ':active': True}
        )
        for item in global_response.get('Items', []):
            if item['guardrailId'] not in guardrail_ids:
                guardrail_ids.append(item['guardrailId'])

        # Fetch all guardrails
        guardrails = []
        for gid in guardrail_ids:
            response = table.get_item(Key={'guardrailId': gid})
            if 'Item' in response and response['Item']['isActive']:
                guardrails.append(response['Item'])

        # Add custom rules from animal config
        if 'guardrails' in animal and 'custom' in animal['guardrails']:
            for custom in animal['guardrails']['custom']:
                guardrails.append({
                    'type': custom['type'],
                    'rule': custom['rule'],
                    'priority': 75  # Custom rules have medium-high priority
                })

        # Sort by priority (higher first)
        guardrails.sort(key=lambda x: x.get('priority', 50), reverse=True)

        return guardrails

    @classmethod
    def format_guardrails_for_prompt(cls, guardrails: List[Dict]) -> str:
        """Format guardrails into text for system prompt"""
        if not guardrails:
            return ""

        sections = {
            'ALWAYS': [],
            'NEVER': [],
            'ENCOURAGE': [],
            'DISCOURAGE': []
        }

        for g in guardrails:
            rule_type = g.get('type', 'ALWAYS')
            rule_text = g.get('rule', '')
            if rule_text:
                sections[rule_type].append(f"• {rule_text}")

        prompt_parts = []

        if sections['ALWAYS']:
            prompt_parts.append("IMPORTANT RULES - ALWAYS:")
            prompt_parts.extend(sections['ALWAYS'])
            prompt_parts.append("")

        if sections['NEVER']:
            prompt_parts.append("IMPORTANT RULES - NEVER:")
            prompt_parts.extend(sections['NEVER'])
            prompt_parts.append("")

        if sections['ENCOURAGE']:
            prompt_parts.append("GUIDELINES - ENCOURAGE:")
            prompt_parts.extend(sections['ENCOURAGE'])
            prompt_parts.append("")

        if sections['DISCOURAGE']:
            prompt_parts.append("GUIDELINES - AVOID:")
            prompt_parts.extend(sections['DISCOURAGE'])
            prompt_parts.append("")

        return "\n".join(prompt_parts)
```

### Updated ChatGPT Integration
```python
# In chatgpt_integration.py

def get_animal_system_prompt(self, animal_id: str) -> str:
    """Get system prompt with dynamic guardrails"""

    # Get base animal data (existing code)
    # ...

    # Get guardrails for this animal
    from .guardrails import GuardrailsManager
    guardrails = GuardrailsManager.get_guardrails_for_animal(animal_id)
    guardrails_text = GuardrailsManager.format_guardrails_for_prompt(guardrails)

    # Build complete prompt
    base_prompt = f"""You are {animal_data.get('name', 'an animal')} at Cougar Mountain Zoo.
{animal_data.get('personality', '')}
Key facts: {animal_data.get('facts', '')}

{guardrails_text}

Remember to stay in character and make the conversation engaging and educational for zoo visitors."""

    return base_prompt
```

## 4. Admin UI Components

### Guardrails Tab Features
1. **List View**
   - Display all guardrails with filters (category, active status, global)
   - Quick enable/disable toggle
   - Search by keywords

2. **Create/Edit Form**
   - Name and description fields
   - Type selector (ALWAYS/NEVER/ENCOURAGE/DISCOURAGE)
   - Rule text input with examples
   - Category selection
   - Priority slider (0-100)
   - Global flag checkbox
   - Keyword tags input

3. **Templates Section**
   - Pre-built guardrail packages
   - One-click apply to animals
   - Customizable after import

4. **Testing Panel**
   - Test guardrails against sample messages
   - Preview system prompt with guardrails
   - Validate rule conflicts

### Animal Config Integration
1. **Guardrails Selection**
   - Multi-select dropdown of available guardrails
   - Show inherited global rules
   - Custom rule input section
   - Priority reordering

2. **Preview Section**
   - Show complete system prompt with guardrails
   - Test conversation with guardrails applied

## 5. Benefits

1. **Flexibility**: Admins can adjust rules without code changes
2. **Consistency**: Global rules ensure baseline safety
3. **Customization**: Animal-specific rules for personality
4. **Auditability**: Track who created/modified rules
5. **Scalability**: Easy to add new rules as needed
6. **Testing**: Preview and test before deployment

## 6. Example Usage

### Creating a Global Family-Friendly Rule
```javascript
POST /guardrails
{
  "name": "Family Friendly Content",
  "type": "ALWAYS",
  "rule": "Always use language appropriate for children and families",
  "category": "content_safety",
  "priority": 100,
  "isGlobal": true,
  "keywords": ["family", "children", "appropriate"]
}
```

### Assigning Guardrails to Pokey
```javascript
PATCH /animal/pokey/config
{
  "guardrails": {
    "selected": ["gr_family_001", "gr_educational_002"],
    "custom": [
      {
        "type": "NEVER",
        "rule": "Never suggest that visitors can pet porcupines"
      }
    ]
  }
}
```

### Result in System Prompt
```
You are Pokey the Porcupine at Cougar Mountain Zoo.
[personality and facts...]

IMPORTANT RULES - ALWAYS:
• Always use language appropriate for children and families
• Always include educational facts when relevant

IMPORTANT RULES - NEVER:
• Never discuss violence, weapons, or harmful activities
• Never suggest that visitors can pet porcupines

GUIDELINES - ENCOURAGE:
• Encourage questions about wildlife and conservation

Remember to stay in character and make the conversation engaging and educational for zoo visitors.
```

## 7. Migration Strategy

1. **Phase 1**: Create DynamoDB table and API endpoints
2. **Phase 2**: Migrate hardcoded rules to database
3. **Phase 3**: Update ChatGPT integration to use dynamic rules
4. **Phase 4**: Add admin UI for management
5. **Phase 5**: Deploy and monitor usage

## 8. Security Considerations

- Only admin/zookeeper roles can manage guardrails
- Audit log for all guardrail changes
- Validation to prevent conflicting rules
- Rate limiting on guardrail API endpoints
- Backup strategy for guardrails table