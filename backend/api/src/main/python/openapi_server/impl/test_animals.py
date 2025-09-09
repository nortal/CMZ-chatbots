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
        "status": "active",
        "softDelete": False
    },
    {
        "animalId": "animal_2", 
        "name": "Koda",
        "species": "Brown Bear",
        "status": "active",
        "softDelete": False
    }
]

MOCK_CONFIGS = {
    "animal_1": {
        "animalConfigId": "config_1",
        "personality": "Energetic and educational, loves talking about speed and hunting techniques",
        "voice": "energetic",
        "aiModel": "claude-3-sonnet",
        "temperature": 0.8,
        "topP": 1.0,
        "toolsEnabled": [],
        "guardrails": {}
    },
    "animal_2": {
        "animalConfigId": "config_2", 
        "personality": "Wise and powerful, enjoys discussing conservation and habitat protection",
        "voice": "wise",
        "aiModel": "claude-3-sonnet", 
        "temperature": 0.6,
        "topP": 1.0,
        "toolsEnabled": [],
        "guardrails": {}
    }
}

def handle_list_animals() -> List[Animal]:
    """Test implementation that returns mock animals"""
    animals = [Animal.from_dict(animal) for animal in MOCK_ANIMALS]
    return animals

def handle_get_animal(animal_id: str) -> Animal:
    """Test implementation that returns a mock animal"""
    for animal_data in MOCK_ANIMALS:
        if animal_data["animalId"] == animal_id:
            return Animal.from_dict(animal_data)
    raise Exception(f"Animal {animal_id} not found")

def handle_get_animal_config(animal_id: str) -> AnimalConfig:
    """Test implementation that returns mock config"""
    if animal_id in MOCK_CONFIGS:
        return AnimalConfig.from_dict(MOCK_CONFIGS[animal_id])
    raise Exception(f"Config for animal {animal_id} not found")

def handle_update_animal_config(animal_id: str, config: AnimalConfig) -> AnimalConfig:
    """Test implementation that simulates config update"""
    if animal_id not in MOCK_CONFIGS:
        raise Exception(f"Animal {animal_id} not found")
    
    # Simulate update - merge the incoming config with existing
    updated_config = MOCK_CONFIGS[animal_id].copy()
    if hasattr(config, 'to_dict'):
        config_dict = config.to_dict()
    else:
        config_dict = dict(config)
    
    # Update only the fields that were provided
    for key, value in config_dict.items():
        if value is not None:
            updated_config[key] = value
    
    MOCK_CONFIGS[animal_id] = updated_config
    return AnimalConfig.from_dict(updated_config)