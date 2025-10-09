"""
Mock data for family operations
"""

# Mock families database
mock_families = {
    "family-001": {
        "familyId": "family-001",
        "name": "Smith Family",
        "parents": ["parent1@test.cmz.org"],
        "students": ["student1@test.cmz.org", "student2@test.cmz.org"],
        "created": {"at": "2024-01-01T00:00:00Z"},
        "modified": {"at": "2024-01-01T00:00:00Z"}
    },
    "family-002": {
        "familyId": "family-002",
        "name": "Johnson Family",
        "parents": ["user_parent_001@cmz.org"],
        "students": [],
        "created": {"at": "2024-01-02T00:00:00Z"},
        "modified": {"at": "2024-01-02T00:00:00Z"}
    }
}

def get_mock_families():
    """Return list of all mock families"""
    return list(mock_families.values())

def get_mock_family_by_id(family_id: str):
    """Get a specific family by ID"""
    return mock_families.get(family_id)

def create_mock_family(family_data: dict):
    """Create a new mock family"""
    import uuid
    from datetime import datetime

    family_id = family_data.get("familyId") or f"family-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat() + "Z"

    family = {
        "familyId": family_id,
        "name": family_data.get("name", "New Family"),
        "parents": family_data.get("parents", []),
        "students": family_data.get("students", []),
        "created": {"at": now},
        "modified": {"at": now}
    }

    mock_families[family_id] = family
    return family

def update_mock_family(family_id: str, update_data: dict):
    """Update an existing mock family"""
    from datetime import datetime

    if family_id not in mock_families:
        return None

    family = mock_families[family_id]

    # Update fields
    if "name" in update_data:
        family["name"] = update_data["name"]
    if "parents" in update_data:
        family["parents"] = update_data["parents"]
    if "students" in update_data:
        family["students"] = update_data["students"]

    family["modified"]["at"] = datetime.utcnow().isoformat() + "Z"

    return family

def delete_mock_family(family_id: str):
    """Delete a mock family"""
    if family_id in mock_families:
        del mock_families[family_id]
        return True
    return False