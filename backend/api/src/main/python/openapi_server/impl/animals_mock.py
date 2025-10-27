"""
Mock Animals Module for Development
Provides mock animal data when database is not available
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Mock animals data
MOCK_ANIMALS = [
    {
        "animalId": "lion_001",
        "name": "Leo",
        "scientificName": "Panthera leo",
        "species": "Lion",
        "habitat": "African Savanna",
        "diet": "Carnivore",
        "conservationStatus": "Vulnerable",
        "description": "The king of the jungle with a magnificent mane",
        "active": True,
        "created": {"at": "2024-01-15T10:00:00Z"},
        "modified": {"at": "2024-03-15T14:30:00Z"}
    },
    {
        "animalId": "elephant_001",
        "name": "Ella",
        "scientificName": "Loxodonta africana",
        "species": "African Elephant",
        "habitat": "African Grasslands",
        "diet": "Herbivore",
        "conservationStatus": "Endangered",
        "description": "The largest land mammal with incredible memory",
        "active": True,
        "created": {"at": "2024-01-16T11:00:00Z"},
        "modified": {"at": "2024-03-14T09:15:00Z"}
    },
    {
        "animalId": "penguin_001",
        "name": "Pablo",
        "scientificName": "Spheniscus humboldti",
        "species": "Humboldt Penguin",
        "habitat": "Coastal Peru and Chile",
        "diet": "Carnivore",
        "conservationStatus": "Vulnerable",
        "description": "A charming aquatic bird that cannot fly but swims excellently",
        "active": True,
        "created": {"at": "2024-01-17T12:00:00Z"},
        "modified": {"at": "2024-03-13T16:45:00Z"}
    },
    {
        "animalId": "giraffe_001",
        "name": "Gerald",
        "scientificName": "Giraffa camelopardalis",
        "species": "Giraffe",
        "habitat": "African Savanna",
        "diet": "Herbivore",
        "conservationStatus": "Vulnerable",
        "description": "The tallest land animal with a unique spotted pattern",
        "active": True,
        "created": {"at": "2024-01-18T13:00:00Z"},
        "modified": {"at": "2024-03-12T11:20:00Z"}
    },
    {
        "animalId": "redpanda_001",
        "name": "Ruby",
        "scientificName": "Ailurus fulgens",
        "species": "Red Panda",
        "habitat": "Temperate forests of the Himalayas",
        "diet": "Omnivore",
        "conservationStatus": "Endangered",
        "description": "A small mammal with rust-colored fur and a ringed tail",
        "active": False,
        "created": {"at": "2024-01-19T14:00:00Z"},
        "modified": {"at": "2024-03-11T08:30:00Z"}
    }
]

# Mock animal configs (for chatbot personalities)
MOCK_ANIMAL_CONFIGS = {
    "lion_001": {
        "animalId": "lion_001",
        "name": "Leo the Lion",
        "personality": "Brave and confident, with a regal demeanor",
        "temperature": 0.7,
        "topP": 0.9,
        "maxTokens": 500,
        "systemPrompt": "You are Leo, a majestic lion at the zoo. You love to share stories about the savanna and your pride.",
        "active": True
    },
    "elephant_001": {
        "animalId": "elephant_001",
        "name": "Ella the Elephant",
        "personality": "Wise and gentle, with an excellent memory",
        "temperature": 0.6,
        "topP": 0.85,
        "maxTokens": 600,
        "systemPrompt": "You are Ella, a wise African elephant. You enjoy sharing your knowledge about elephant families and conservation.",
        "active": True
    },
    "penguin_001": {
        "animalId": "penguin_001",
        "name": "Pablo the Penguin",
        "personality": "Playful and energetic, loves to waddle and swim",
        "temperature": 0.8,
        "topP": 0.95,
        "maxTokens": 400,
        "systemPrompt": "You are Pablo, a Humboldt penguin. You love to talk about swimming, fish, and your colony friends.",
        "active": True
    }
}


def get_mock_animals(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get list of mock animals with optional status filter

    Args:
        status: Optional filter for active/inactive animals

    Returns:
        List of animal dictionaries
    """
    logger.info(f"Returning mock animals data (status filter: {status})")

    if status == "active":
        return [a for a in MOCK_ANIMALS if a.get("active", True)]
    elif status == "inactive":
        return [a for a in MOCK_ANIMALS if not a.get("active", True)]

    return MOCK_ANIMALS


def get_mock_animal_config(animal_id: str) -> Optional[Dict[str, Any]]:
    """
    Get mock animal configuration by ID

    Args:
        animal_id: Animal ID to retrieve

    Returns:
        Animal config dictionary or None if not found
    """
    logger.info(f"Returning mock animal config for: {animal_id}")
    return MOCK_ANIMAL_CONFIGS.get(animal_id)


def update_mock_animal_config(animal_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update mock animal configuration

    Args:
        animal_id: Animal ID to update
        updates: Dictionary of updates to apply

    Returns:
        Updated config or None if not found
    """
    logger.info(f"Updating mock animal config for: {animal_id}")

    if animal_id in MOCK_ANIMAL_CONFIGS:
        config = MOCK_ANIMAL_CONFIGS[animal_id]
        config.update(updates)
        config["modified"] = {"at": datetime.utcnow().isoformat() + "Z"}
        return config

    return None


def create_mock_animal(animal_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new mock animal

    Args:
        animal_data: Animal data to create

    Returns:
        Created animal data with generated ID
    """
    import uuid

    # Generate a unique ID if not provided
    if "animalId" not in animal_data:
        animal_data["animalId"] = f"animal_{uuid.uuid4().hex[:8]}"

    # Add timestamps
    now = datetime.utcnow().isoformat() + "Z"
    animal_data["created"] = {"at": now}
    animal_data["modified"] = {"at": now}

    # Add to mock data
    MOCK_ANIMALS.append(animal_data)

    logger.info(f"Created mock animal: {animal_data['animalId']}")
    return animal_data