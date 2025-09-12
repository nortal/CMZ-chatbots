"""
Enhanced test utilities and mock repositories for comprehensive testing.
PR003946-95: Test utilities and fixtures enhancement

Provides mock implementations, test data generators, and utility functions
to support comprehensive unit testing of the CMZ API.
"""
import uuid
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import MagicMock


class MockDynamoDBRepository:
    """Mock DynamoDB repository for testing without external dependencies."""
    
    def __init__(self, table_name: str, primary_key: str):
        self.table_name = table_name
        self.primary_key = primary_key
        self.data: Dict[str, Dict] = {}
        self.soft_deleted: Dict[str, Dict] = {}
    
    def create(self, item: Dict) -> Dict:
        """Create a new item in the mock store."""
        if self.primary_key not in item:
            item[self.primary_key] = f"mock_{uuid.uuid4().hex[:8]}"
        
        # Add audit fields
        now = datetime.now(timezone.utc).isoformat()
        item.setdefault("created", {"at": now, "by": {"userId": "test_user"}})
        item["modified"] = {"at": now, "by": {"userId": "test_user"}}
        
        item_id = item[self.primary_key]
        self.data[item_id] = dict(item)
        return dict(item)
    
    def get(self, item_id: str) -> Optional[Dict]:
        """Get an item by ID."""
        return self.data.get(item_id)
    
    def list(self, hide_soft_deleted: bool = True) -> List[Dict]:
        """List all items."""
        if hide_soft_deleted:
            return [item for item in self.data.values() 
                   if not item.get("softDelete", {}).get("flag", False)]
        return list(self.data.values())
    
    def update(self, item_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing item."""
        if item_id not in self.data:
            return None
        
        item = self.data[item_id].copy()
        item.update(updates)
        
        # Update modified timestamp
        now = datetime.now(timezone.utc).isoformat()
        item["modified"] = {"at": now, "by": {"userId": "test_user"}}
        
        self.data[item_id] = item
        return item
    
    def delete(self, item_id: str) -> bool:
        """Hard delete an item."""
        if item_id in self.data:
            del self.data[item_id]
            return True
        return False
    
    def soft_delete(self, item_id: str) -> bool:
        """Soft delete an item."""
        if item_id in self.data:
            now = datetime.now(timezone.utc).isoformat()
            self.data[item_id]["softDelete"] = {
                "flag": True,
                "at": now,
                "by": {"userId": "test_user"}
            }
            return True
        return False
    
    def clear(self):
        """Clear all data (for test cleanup)."""
        self.data.clear()
        self.soft_deleted.clear()


class TestDataGenerator:
    """Generate realistic test data for various entity types."""
    
    @staticmethod
    def create_user_data(override: Dict = None) -> Dict:
        """Generate realistic user test data."""
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        base_data = {
            "userId": user_id,
            "displayName": f"Test User {random.randint(1, 999)}",
            "email": f"testuser{random.randint(1, 999)}@test.cmz.org",
            "role": random.choice(["member", "parent", "keeper", "admin"]),
            "userType": random.choice(["student", "parent", "none"]),
            "created": {
                "at": datetime.now(timezone.utc).isoformat(),
                "by": {"userId": "system", "displayName": "System"}
            },
            "modified": {
                "at": datetime.now(timezone.utc).isoformat(),
                "by": {"userId": "system", "displayName": "System"}
            }
        }
        
        if override:
            base_data.update(override)
        
        return base_data
    
    @staticmethod
    def create_family_data(override: Dict = None) -> Dict:
        """Generate realistic family test data."""
        family_id = f"family_{uuid.uuid4().hex[:8]}"
        base_data = {
            "familyId": family_id,
            "familyName": f"Test Family {random.randint(1, 999)}",
            "parents": [f"user_parent_{random.randint(1, 99)}"],
            "students": [
                f"user_student_{random.randint(100, 199)}",
                f"user_student_{random.randint(200, 299)}"
            ],
            "created": {
                "at": datetime.now(timezone.utc).isoformat(),
                "by": {"userId": "system", "displayName": "System"}
            },
            "modified": {
                "at": datetime.now(timezone.utc).isoformat(),
                "by": {"userId": "system", "displayName": "System"}
            }
        }
        
        if override:
            base_data.update(override)
        
        return base_data
    
    @staticmethod
    def create_animal_data(override: Dict = None) -> Dict:
        """Generate realistic animal test data."""
        animal_id = f"animal_{uuid.uuid4().hex[:8]}"
        animals = [
            ("Leo", "Lion", "African Savanna", "brave,majestic,educational"),
            ("Zara", "Zebra", "African Plains", "playful,energetic,curious"),
            ("Ella", "Elephant", "African Bush", "wise,gentle,family-oriented"),
            ("Max", "Monkey", "Tropical Forest", "mischievous,intelligent,social"),
            ("Bella", "Bear", "Forest", "protective,strong,hibernating")
        ]
        
        name, species, habitat, personality = random.choice(animals)
        base_data = {
            "animalId": animal_id,
            "animalName": f"{name} the {species}",
            "species": species,
            "habitat": habitat,
            "description": f"A magnificent {species.lower()} living in the {habitat.lower()}",
            "personality": personality,
            "chatbotConfig": {
                "enabled": random.choice([True, False]),
                "model": random.choice(["claude-3-sonnet", "claude-3-haiku"]),
                "temperature": round(random.uniform(0.3, 0.9), 1),
                "personalityTraits": personality.split(",")
            },
            "created": {
                "at": datetime.now(timezone.utc).isoformat(),
                "by": {"userId": "system", "displayName": "System"}
            },
            "modified": {
                "at": datetime.now(timezone.utc).isoformat(),
                "by": {"userId": "system", "displayName": "System"}
            }
        }
        
        if override:
            base_data.update(override)
        
        return base_data
    
    @staticmethod
    def create_conversation_data(override: Dict = None) -> Dict:
        """Generate realistic conversation test data."""
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        base_data = {
            "conversationId": conversation_id,
            "userId": f"user_{uuid.uuid4().hex[:8]}",
            "animalId": f"animal_{uuid.uuid4().hex[:8]}",
            "messages": [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "sender": "user",
                    "message": "Hello! Tell me about yourself."
                },
                {
                    "timestamp": (datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat(),
                    "sender": "animal",
                    "message": "Hello there! I'm excited to chat with you about my life here at the zoo!"
                }
            ],
            "status": "active",
            "created": {
                "at": datetime.now(timezone.utc).isoformat(),
                "by": {"userId": "system", "displayName": "System"}
            },
            "modified": {
                "at": datetime.now(timezone.utc).isoformat(),
                "by": {"userId": "system", "displayName": "System"}
            }
        }
        
        if override:
            base_data.update(override)
        
        return base_data


class BoundaryValueTestGenerator:
    """Enhanced boundary value generator for comprehensive edge case testing."""
    
    @staticmethod
    def get_invalid_ids() -> List[str]:
        """Generate invalid ID values for testing."""
        return [
            "",                          # Empty string
            " ",                         # Whitespace only
            "   ",                       # Multiple spaces
            "\t",                        # Tab character
            "\n",                        # Newline character
            "invalid/id/with/slashes",   # Path-like structure
            "invalid@id#with$symbols",   # Special characters
            "id with spaces",            # Spaces in ID
            "A" * 200,                   # Extremely long ID
            "123",                       # Numbers only
            "ID_WITH_ALL_CAPS",          # All uppercase
            "mixed_Case_ID_123",         # Mixed case
            "unicode_id_测试",           # Unicode characters
            "id-with-dashes-everywhere", # Many dashes
            "id.with.dots.everywhere"    # Many dots
        ]
    
    @staticmethod
    def get_invalid_emails() -> List[str]:
        """Generate invalid email values for testing."""
        return [
            "",                          # Empty
            "invalid.email",             # No @ symbol
            "@domain.com",               # Missing local part
            "user@",                     # Missing domain
            "user@domain",               # Missing TLD
            "user name@domain.com",      # Space in local part
            "user@domain..com",          # Double dot in domain
            "user@domain.c",             # TLD too short
            "user@.domain.com",          # Domain starts with dot
            "user@domain.com.",          # Ends with dot
            "user@@domain.com",          # Double @ symbol
            "user@domain@com",           # Multiple @ symbols
            "A" * 100 + "@domain.com",   # Extremely long local part
        ]
    
    @staticmethod
    def get_invalid_pagination_values() -> List[Any]:
        """Generate invalid pagination values for testing."""
        return [
            -1,                          # Negative number
            0,                           # Zero
            "invalid",                   # Non-numeric string
            "",                          # Empty string
            " ",                         # Whitespace
            None,                        # None value
            [],                          # List
            {},                          # Dictionary
            3.14,                        # Float (might be valid or invalid depending on implementation)
            "10.5",                      # Numeric string with decimal
            "1000000",                   # Extremely large number as string
            -999999,                     # Large negative number
        ]
    
    @staticmethod
    def get_long_strings(base_length: int = 255) -> List[str]:
        """Generate strings of various lengths for boundary testing."""
        return [
            "a" * (base_length - 1),     # Just under limit
            "a" * base_length,           # At limit
            "a" * (base_length + 1),     # Just over limit
            "a" * (base_length * 2),     # Double limit
            "a" * 1000,                  # Very long
            "a" * 10000,                 # Extremely long
            "测试" * (base_length // 2),  # Unicode characters
            "🦁" * (base_length // 4),    # Emoji characters
            "A" * base_length,           # All caps
            "1" * base_length,           # All numbers
        ]
    
    @staticmethod
    def get_special_characters() -> List[str]:
        """Generate strings with special characters for testing."""
        return [
            "<script>alert('xss')</script>",           # XSS attempt
            "'; DROP TABLE users; --",                 # SQL injection attempt
            "test\nwith\nnewlines",                   # Newlines
            "test\twith\ttabs",                       # Tabs
            '"quoted string"',                         # Quotes
            "'single quoted'",                        # Single quotes
            "back\\slash\\test",                      # Backslashes
            "unicode: àáâãäåæç",                      # Unicode accents
            "emoji: 🦁🐅🐘🦅🐧",                      # Emojis
            "mixed: test123!@#$%^&*()",               # Mixed characters
            "json: {\"key\": \"value\"}",             # JSON-like structure
            "xml: <tag>content</tag>",                # XML-like structure
        ]


class MockAuthenticationHelper:
    """Helper for mocking authentication in tests."""
    
    @staticmethod
    def create_mock_user(role: str = "member", user_type: str = "student") -> Dict:
        """Create a mock authenticated user."""
        return {
            "userId": f"mock_user_{uuid.uuid4().hex[:8]}",
            "email": f"mockuser@test.cmz.org",
            "displayName": "Mock Test User",
            "role": role,
            "userType": user_type,
            "authenticated": True
        }
    
    @staticmethod
    def create_mock_jwt_token(user: Dict = None) -> str:
        """Create a mock JWT token for testing."""
        if not user:
            user = MockAuthenticationHelper.create_mock_user()
        
        # This is a mock token - not a real JWT
        return f"mock.jwt.token.{user['userId']}"
    
    @staticmethod
    def create_auth_headers(user: Dict = None) -> Dict:
        """Create authentication headers for API testing."""
        if not user:
            user = MockAuthenticationHelper.create_mock_user()
        
        token = MockAuthenticationHelper.create_mock_jwt_token(user)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }


class TestDatabaseManager:
    """Manager for test database state across test sessions."""
    
    def __init__(self):
        self.repositories: Dict[str, MockDynamoDBRepository] = {}
    
    def get_repository(self, table_name: str, primary_key: str) -> MockDynamoDBRepository:
        """Get or create a mock repository."""
        key = f"{table_name}:{primary_key}"
        if key not in self.repositories:
            self.repositories[key] = MockDynamoDBRepository(table_name, primary_key)
        return self.repositories[key]
    
    def clear_all(self):
        """Clear all test data."""
        for repo in self.repositories.values():
            repo.clear()
    
    def seed_test_data(self):
        """Seed repositories with consistent test data."""
        # Create test users
        user_repo = self.get_repository("quest-dev-user", "userId")
        for i in range(5):
            user_data = TestDataGenerator.create_user_data({
                "userId": f"test_user_{i:03d}",
                "displayName": f"Test User {i}",
                "email": f"testuser{i:03d}@test.cmz.org"
            })
            user_repo.create(user_data)
        
        # Create test families
        family_repo = self.get_repository("quest-dev-family", "familyId")
        for i in range(3):
            family_data = TestDataGenerator.create_family_data({
                "familyId": f"test_family_{i:03d}",
                "familyName": f"Test Family {i}",
                "parents": [f"test_user_{i*2:03d}"],
                "students": [f"test_user_{i*2+1:03d}"]
            })
            family_repo.create(family_data)
        
        # Create test animals
        animal_repo = self.get_repository("quest-dev-animal", "animalId")
        for i in range(4):
            animal_data = TestDataGenerator.create_animal_data({
                "animalId": f"test_animal_{i:03d}"
            })
            animal_repo.create(animal_data)


# Global test database manager instance
test_db_manager = TestDatabaseManager()