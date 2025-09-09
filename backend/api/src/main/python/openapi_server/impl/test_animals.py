"""
Test handlers for animal endpoints that work without AWS credentials
"""
from typing import List, Tuple
from openapi_server.models.animal import Animal
from openapi_server.models.animal_config import AnimalConfig
from openapi_server.models.animal_details import AnimalDetails
from openapi_server.models.error import Error

# Mock data for testing
MOCK_ANIMALS = [
    {
        "animalId": "animal_1",
        "name": "Simba",
        "species": "Lion", 
        "status": "active"
    },
    {
        "animalId": "animal_2", 
        "name": "Koda",
        "species": "Brown Bear",
        "status": "active"
    }
]

MOCK_CONFIGS = {
    "animal_1": {
        "animalId": "animal_1",
        "personality": "friendly",
        "greeting": "Hello! I'm Simba the lion!"
    },
    "animal_2": {
        "animalId": "animal_2", 
        "personality": "playful",
        "greeting": "Hi there! I'm Koda the bear!"
    }
}

def handle_list_animals() -> Tuple[List[Animal], int]:
    """Test implementation that returns mock animals"""
    animals = [Animal.from_dict(animal) for animal in MOCK_ANIMALS]
    return animals, 200

def handle_get_animal(animal_id: str) -> Tuple[Animal, int]:
    """Test implementation that returns a mock animal"""
    for animal_data in MOCK_ANIMALS:
        if animal_data["animalId"] == animal_id:
            return Animal.from_dict(animal_data), 200
    return Error(error=f"Animal {animal_id} not found"), 404

def handle_get_animal_config(animal_id: str) -> Tuple[AnimalConfig, int]:
    """Test implementation that returns mock config"""
    if animal_id in MOCK_CONFIGS:
        return AnimalConfig.from_dict(MOCK_CONFIGS[animal_id]), 200
    return Error(error=f"Config for animal {animal_id} not found"), 404

def handle_update_animal_config(animal_id: str, config: AnimalConfig) -> Tuple[dict, int]:
    """Test implementation that simulates config update"""
    if animal_id not in MOCK_CONFIGS:
        return Error(error=f"Animal {animal_id} not found"), 404
    
    # Simulate update
    MOCK_CONFIGS[animal_id] = config.to_dict()
    return {"message": f"Config updated for {animal_id}"}, 200