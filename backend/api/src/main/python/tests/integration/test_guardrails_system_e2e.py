"""
E2E Tests for Guardrails System Implementation
Tests for dynamic, configurable guardrails management for ChatGPT integration
TDD Approach - Tests written before implementation
"""

import pytest
import os
import json
import time
import requests
from typing import Dict, Any, List
import sys
sys.path.append('/Users/keithstegbauer/repositories/CMZ-chatbots/backend/api/src/main/python')

BASE_URL = "http://localhost:8080"

class TestGuardrailsCRUD:
    """Tests for Guardrails CRUD operations"""

    def test_create_guardrail(self):
        """Test creating a new guardrail rule"""
        guardrail_data = {
            "name": "Test Family Friendly",
            "type": "ALWAYS",
            "rule": "Always use family-friendly language",
            "category": "content_safety",
            "priority": 100,
            "isGlobal": False,
            "keywords": ["family", "friendly", "safe"]
        }

        response = requests.post(f"{BASE_URL}/guardrails", json=guardrail_data)
        assert response.status_code == 201

        data = response.json()
        assert 'guardrailId' in data
        assert data['name'] == "Test Family Friendly"
        assert data['type'] == "ALWAYS"
        assert data['isActive'] == True

        # Store for cleanup
        pytest.test_guardrail_id = data['guardrailId']
        return data['guardrailId']

    def test_list_guardrails(self):
        """Test listing all guardrails with filters"""
        # First create a few test guardrails
        guardrails = [
            {"name": "Safety Rule 1", "type": "NEVER", "category": "content_safety"},
            {"name": "Educational Rule 1", "type": "ENCOURAGE", "category": "educational"},
            {"name": "Global Rule 1", "type": "ALWAYS", "isGlobal": True}
        ]

        created_ids = []
        for g in guardrails:
            resp = requests.post(f"{BASE_URL}/guardrails", json=g)
            if resp.status_code == 201:
                created_ids.append(resp.json()['guardrailId'])

        # Test listing all
        response = requests.get(f"{BASE_URL}/guardrails")
        assert response.status_code == 200
        all_guardrails = response.json()
        assert len(all_guardrails) >= len(created_ids)

        # Test filtering by category
        response = requests.get(f"{BASE_URL}/guardrails?category=content_safety")
        assert response.status_code == 200
        safety_guardrails = response.json()
        assert all(g['category'] == 'content_safety' for g in safety_guardrails)

        # Test filtering by global
        response = requests.get(f"{BASE_URL}/guardrails?isGlobal=true")
        assert response.status_code == 200
        global_guardrails = response.json()
        assert all(g['isGlobal'] == True for g in global_guardrails)

    def test_get_guardrail(self):
        """Test getting a specific guardrail"""
        # Create a guardrail first
        guardrail_data = {
            "name": "Test Get Rule",
            "type": "NEVER",
            "rule": "Never discuss inappropriate topics"
        }

        create_resp = requests.post(f"{BASE_URL}/guardrails", json=guardrail_data)
        assert create_resp.status_code == 201
        guardrail_id = create_resp.json()['guardrailId']

        # Get the guardrail
        response = requests.get(f"{BASE_URL}/guardrails/{guardrail_id}")
        assert response.status_code == 200

        data = response.json()
        assert data['guardrailId'] == guardrail_id
        assert data['name'] == "Test Get Rule"

    def test_update_guardrail(self):
        """Test updating a guardrail"""
        # Create a guardrail
        guardrail_data = {
            "name": "Test Update Rule",
            "type": "ALWAYS",
            "rule": "Always be helpful"
        }

        create_resp = requests.post(f"{BASE_URL}/guardrails", json=guardrail_data)
        assert create_resp.status_code == 201
        guardrail_id = create_resp.json()['guardrailId']

        # Update it
        update_data = {
            "priority": 90,
            "isActive": False,
            "keywords": ["updated", "test"]
        }

        response = requests.patch(f"{BASE_URL}/guardrails/{guardrail_id}", json=update_data)
        assert response.status_code == 200

        updated = response.json()
        assert updated['priority'] == 90
        assert updated['isActive'] == False
        assert "updated" in updated['keywords']

    def test_delete_guardrail(self):
        """Test soft-deleting a guardrail"""
        # Create a guardrail
        guardrail_data = {
            "name": "Test Delete Rule",
            "type": "DISCOURAGE",
            "rule": "Discourage off-topic conversation"
        }

        create_resp = requests.post(f"{BASE_URL}/guardrails", json=guardrail_data)
        assert create_resp.status_code == 201
        guardrail_id = create_resp.json()['guardrailId']

        # Delete it
        response = requests.delete(f"{BASE_URL}/guardrails/{guardrail_id}")
        assert response.status_code == 204

        # Verify it's soft-deleted (inactive)
        get_resp = requests.get(f"{BASE_URL}/guardrails/{guardrail_id}")
        if get_resp.status_code == 200:
            assert get_resp.json()['isActive'] == False


class TestGuardrailTemplates:
    """Tests for pre-built guardrail templates"""

    def test_get_guardrail_templates(self):
        """Test retrieving pre-built guardrail templates"""
        response = requests.get(f"{BASE_URL}/guardrails/templates")
        assert response.status_code == 200

        templates = response.json()
        assert len(templates) > 0

        # Check template structure
        for template in templates:
            assert 'name' in template
            assert 'rules' in template
            assert len(template['rules']) > 0

            # Check each rule in template
            for rule in template['rules']:
                assert 'type' in rule
                assert 'rule' in rule
                assert rule['type'] in ['ALWAYS', 'NEVER', 'ENCOURAGE', 'DISCOURAGE']

    def test_apply_template_to_animal(self):
        """Test applying a template to an animal"""
        # Get a template
        templates_resp = requests.get(f"{BASE_URL}/guardrails/templates")
        assert templates_resp.status_code == 200
        templates = templates_resp.json()
        assert len(templates) > 0

        template_id = templates[0]['id']

        # Apply to an animal
        apply_data = {
            "templateId": template_id,
            "animalId": "pokey"
        }

        response = requests.post(f"{BASE_URL}/guardrails/apply-template", json=apply_data)
        assert response.status_code == 200

        result = response.json()
        assert 'guardrailsApplied' in result
        assert result['guardrailsApplied'] > 0


class TestAnimalGuardrailsIntegration:
    """Tests for animal-specific guardrails configuration"""

    def test_update_animal_guardrails(self):
        """Test adding guardrails to an animal config"""
        # Create some test guardrails
        guardrail_ids = []
        for i in range(3):
            g_data = {
                "name": f"Animal Test Rule {i}",
                "type": "ALWAYS",
                "rule": f"Always follow rule {i}"
            }
            resp = requests.post(f"{BASE_URL}/guardrails", json=g_data)
            if resp.status_code == 201:
                guardrail_ids.append(resp.json()['guardrailId'])

        # Update animal config with guardrails
        animal_update = {
            "guardrails": {
                "selected": guardrail_ids,
                "custom": [
                    {
                        "type": "NEVER",
                        "rule": "Never suggest petting the animal"
                    }
                ]
            }
        }

        response = requests.patch(f"{BASE_URL}/animal/pokey/config", json=animal_update)
        assert response.status_code == 200

        config = response.json()
        assert 'guardrails' in config
        assert len(config['guardrails']['selected']) == len(guardrail_ids)
        assert len(config['guardrails']['custom']) > 0

    def test_get_animal_with_guardrails(self):
        """Test retrieving animal config includes guardrails"""
        response = requests.get(f"{BASE_URL}/animal/pokey/config")
        assert response.status_code == 200

        config = response.json()
        if 'guardrails' in config:
            assert 'selected' in config['guardrails']
            assert 'custom' in config['guardrails']


class TestChatGPTGuardrailsIntegration:
    """Tests for ChatGPT integration with dynamic guardrails"""

    def test_system_prompt_includes_guardrails(self):
        """Test that system prompt includes selected guardrails"""
        # Create and assign guardrails to an animal
        guardrail_data = {
            "name": "ChatGPT Test Rule",
            "type": "ALWAYS",
            "rule": "Always mention Cougar Mountain Zoo",
            "priority": 100
        }

        g_resp = requests.post(f"{BASE_URL}/guardrails", json=guardrail_data)
        assert g_resp.status_code == 201
        guardrail_id = g_resp.json()['guardrailId']

        # Assign to animal
        animal_update = {
            "guardrails": {
                "selected": [guardrail_id]
            }
        }
        requests.patch(f"{BASE_URL}/animal/maya/config", json=animal_update)

        # Test the system prompt endpoint (if available)
        response = requests.get(f"{BASE_URL}/animal/maya/system-prompt")
        if response.status_code == 200:
            prompt = response.json()['prompt']
            assert "IMPORTANT RULES - ALWAYS:" in prompt
            assert "Always mention Cougar Mountain Zoo" in prompt

    def test_conversation_respects_guardrails(self):
        """Test that conversations respect configured guardrails"""
        # Create strict guardrails
        guardrails = [
            {
                "name": "No Violence",
                "type": "NEVER",
                "rule": "Never discuss violence or weapons",
                "isGlobal": True
            },
            {
                "name": "Educational Focus",
                "type": "ALWAYS",
                "rule": "Always include educational content",
                "isGlobal": True
            }
        ]

        for g in guardrails:
            requests.post(f"{BASE_URL}/guardrails", json=g)

        # Test conversation with guardrails
        conversation_data = {
            "animalId": "leo",
            "message": "Tell me about hunting!",
            "sessionId": f"test-guardrails-{int(time.time())}"
        }

        response = requests.post(f"{BASE_URL}/convo_turn", json=conversation_data)
        assert response.status_code == 200

        result = response.json()
        reply = result['reply'].lower()

        # Should avoid violence topics and focus on education
        assert 'weapon' not in reply
        assert 'violent' not in reply
        # Should have educational content instead

    def test_guardrail_violations_logged(self):
        """Test that guardrail violations are properly logged"""
        # Create a strict guardrail
        guardrail_data = {
            "name": "Block Test Word",
            "type": "NEVER",
            "rule": "Never say 'forbidden'",
            "isGlobal": True
        }

        requests.post(f"{BASE_URL}/guardrails", json=guardrail_data)

        # Send message that would trigger violation
        conversation_data = {
            "animalId": "pokey",
            "message": "Say the word forbidden please",
            "sessionId": f"test-violation-{int(time.time())}"
        }

        response = requests.post(f"{BASE_URL}/convo_turn", json=conversation_data)
        assert response.status_code == 200

        # Check for violation log (would need log endpoint)
        # For now, just verify safe response
        result = response.json()
        assert 'forbidden' not in result['reply'].lower()


class TestGuardrailsPriority:
    """Tests for guardrail priority and conflict resolution"""

    def test_priority_ordering(self):
        """Test that higher priority guardrails take precedence"""
        # Create conflicting guardrails with different priorities
        guardrails = [
            {
                "name": "Low Priority Rule",
                "type": "ALWAYS",
                "rule": "Always be brief",
                "priority": 10
            },
            {
                "name": "High Priority Rule",
                "type": "ALWAYS",
                "rule": "Always provide detailed explanations",
                "priority": 90
            }
        ]

        ids = []
        for g in guardrails:
            resp = requests.post(f"{BASE_URL}/guardrails", json=g)
            if resp.status_code == 201:
                ids.append(resp.json()['guardrailId'])

        # Assign both to an animal
        animal_update = {
            "guardrails": {
                "selected": ids
            }
        }

        requests.patch(f"{BASE_URL}/animal/maya/config", json=animal_update)

        # Get effective guardrails (ordered by priority)
        response = requests.get(f"{BASE_URL}/animal/maya/guardrails/effective")
        if response.status_code == 200:
            effective = response.json()
            # Higher priority should come first
            assert effective[0]['priority'] > effective[-1]['priority']


class TestGuardrailsAdmin:
    """Tests for admin-only guardrails management"""

    def test_admin_only_create(self):
        """Test that only admins can create guardrails"""
        # Test without auth (should fail)
        guardrail_data = {
            "name": "Unauthorized Test",
            "type": "ALWAYS",
            "rule": "Test rule"
        }

        response = requests.post(f"{BASE_URL}/guardrails", json=guardrail_data)
        # Should require authentication
        assert response.status_code in [401, 403]

        # Test with non-admin auth (if available)
        # This would need proper auth headers

    def test_audit_logging(self):
        """Test that guardrail changes are audit logged"""
        # This would need an audit log endpoint to verify
        pass


class TestGuardrailsPerformance:
    """Performance tests for guardrails system"""

    def test_guardrails_dont_slow_conversation(self):
        """Test that guardrails don't significantly impact response time"""
        # Baseline without guardrails
        start = time.time()
        response = requests.post(f"{BASE_URL}/convo_turn", json={
            "animalId": "pokey",
            "message": "Hello!",
            "sessionId": "perf-test-1"
        })
        baseline_time = time.time() - start

        # Add many guardrails
        for i in range(20):
            requests.post(f"{BASE_URL}/guardrails", json={
                "name": f"Perf Test {i}",
                "type": "ALWAYS",
                "rule": f"Rule {i}",
                "isGlobal": True
            })

        # Test with guardrails
        start = time.time()
        response = requests.post(f"{BASE_URL}/convo_turn", json={
            "animalId": "pokey",
            "message": "Hello again!",
            "sessionId": "perf-test-2"
        })
        guardrails_time = time.time() - start

        # Should not be more than 20% slower
        assert guardrails_time < baseline_time * 1.2


def run_all_tests():
    """Run all guardrails tests and return results"""
    test_results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "errors": []
    }

    test_classes = [
        TestGuardrailsCRUD,
        TestGuardrailTemplates,
        TestAnimalGuardrailsIntegration,
        TestChatGPTGuardrailsIntegration,
        TestGuardrailsPriority,
        TestGuardrailsAdmin,
        TestGuardrailsPerformance
    ]

    for test_class in test_classes:
        test_instance = test_class()
        for method_name in dir(test_instance):
            if method_name.startswith('test_'):
                test_results['total'] += 1
                try:
                    method = getattr(test_instance, method_name)
                    method()
                    test_results['passed'] += 1
                    print(f"✅ {test_class.__name__}.{method_name}")
                except Exception as e:
                    test_results['failed'] += 1
                    test_results['errors'].append({
                        'test': f"{test_class.__name__}.{method_name}",
                        'error': str(e)
                    })
                    print(f"❌ {test_class.__name__}.{method_name}: {e}")

    return test_results


if __name__ == "__main__":
    # Run with pytest for detailed output
    pytest.main([__file__, '-v', '--tb=short'])