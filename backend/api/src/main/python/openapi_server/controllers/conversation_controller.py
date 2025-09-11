import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.convo_history import ConvoHistory  # noqa: E501
from openapi_server.models.convo_turn_request import ConvoTurnRequest  # noqa: E501
from openapi_server.models.convo_turn_response import ConvoTurnResponse  # noqa: E501
from openapi_server.models.convo_turn_response_turn import ConvoTurnResponseTurn  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.summarize_request import SummarizeRequest  # noqa: E501
from openapi_server.models.summary import Summary  # noqa: E501
from openapi_server import util
from datetime import datetime
import uuid
import time
import json
import os

def _load_animal_personalities():
    """Load animal personalities from configuration file"""
    try:
        # Get the directory of this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to openapi_server, then into config
        config_path = os.path.join(current_dir, '..', 'config', 'animal_personalities.json')
        
        with open(config_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Fallback to basic personalities if config file is missing
        return {
            "animal_1": {
                "name": "Zoo Friend",
                "personality": "Friendly and educational",
                "responses": {
                    "default": "Hello! I'm an animal here at the zoo. I'd love to share knowledge about wildlife and conservation with you!"
                }
            }
        }

# Load animal personalities from configuration
ANIMAL_PERSONALITIES = _load_animal_personalities()

def _generate_ai_response(animal_id, message, context_summary=None):
    """Generate a realistic AI response based on animal personality"""
    
    # Get animal personality or use default
    animal = ANIMAL_PERSONALITIES.get(animal_id, {
        "name": "Zoo Friend",
        "personality": "Friendly and educational",
        "responses": {
            "default": "Hello! I'm an animal here at the zoo. I'd love to share knowledge about wildlife and conservation with you!"
        }
    })
    
    message_lower = message.lower()
    
    # Simple keyword matching for different response types
    if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
        response_key = "greeting"
    elif any(word in message_lower for word in ["hunt", "hunting", "predator", "prey"]):
        response_key = "hunting"
    elif any(word in message_lower for word in ["eat", "food", "diet", "meal"]):
        response_key = "diet"
    elif any(word in message_lower for word in ["sleep", "hibernat", "winter", "rest"]):
        response_key = "hibernation"
    elif any(word in message_lower for word in ["home", "habitat", "environment", "conservation"]):
        response_key = "habitat"
    else:
        response_key = "default"
    
    # Get the appropriate response or fall back to default
    response = animal["responses"].get(response_key, animal["responses"].get("default", 
        "That's interesting! I'd love to help you learn more about wildlife and conservation."))
    
    # Add some variation to make responses feel more natural
    if context_summary and "previous" in context_summary.lower():
        response = f"Building on our previous conversation, {response.lower()}"
    
    return response

def convo_history_delete(id):  # noqa: E501
    """Delete conversation history (GDPR) (backlog)

     # noqa: E501

    :param id: Conversation/session id
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def convo_history_get(animalid=None, userid=None, limit=None):  # noqa: E501
    """Get conversation history (backlog)

     # noqa: E501

    :param animalid: 
    :type animalid: str
    :param userid: 
    :type userid: str
    :param limit: 
    :type limit: int

    :rtype: Union[ConvoHistory, Tuple[ConvoHistory, int], Tuple[ConvoHistory, int, Dict[str, str]]
    """
    return 'do some magic!'


def convo_turn_post(body):  # noqa: E501
    """Send a conversation turn and get AI reply

     # noqa: E501

    :param convo_turn_request: 
    :type convo_turn_request: dict | bytes

    :rtype: Union[ConvoTurnResponse, Tuple[ConvoTurnResponse, int], Tuple[ConvoTurnResponse, int, Dict[str, str]]
    """
    try:
        convo_turn_request = body
        if connexion.request.is_json:
            convo_turn_request = ConvoTurnRequest.from_dict(connexion.request.get_json())  # noqa: E501
        
        # Extract request data - handle both object attributes and dict keys
        if hasattr(convo_turn_request, 'animal_id'):
            # Use object attributes directly
            animal_id = convo_turn_request.animal_id
            message = convo_turn_request.message
            context_summary = convo_turn_request.context_summary
        elif hasattr(convo_turn_request, 'to_dict'):
            # Convert to dict and use camelCase keys
            request_data = convo_turn_request.to_dict()
            animal_id = request_data.get('animalId')
            message = request_data.get('message')
            context_summary = request_data.get('contextSummary')
        else:
            # Use as dict directly
            request_data = dict(convo_turn_request)
            animal_id = request_data.get('animalId')
            message = request_data.get('message')
            context_summary = request_data.get('contextSummary')
        
        # Validate required fields
        if not animal_id:
            return Error(code='VALIDATION_ERROR', message='animalId is required'), 400
        if not message:
            return Error(code='VALIDATION_ERROR', message='message is required'), 400
        
        # Generate AI response
        start_time = time.time()
        ai_reply = _generate_ai_response(animal_id, message, context_summary)
        end_time = time.time()
        
        # Calculate latency in milliseconds
        latency_ms = int((end_time - start_time) * 1000)
        
        # Simulate token counts (in production, these would come from the AI service)
        prompt_tokens = len(message.split()) + 50  # Base prompt overhead
        completion_tokens = len(ai_reply.split())
        
        # Generate conversation turn ID
        convo_turn_id = f"turn_{str(uuid.uuid4()).replace('-', '_')}"
        
        # Create turn metadata
        turn = ConvoTurnResponseTurn(
            convo_turn_id=convo_turn_id,
            timestamp=datetime.utcnow(),
            tokens_prompt=prompt_tokens,
            tokens_completion=completion_tokens,
            latency_ms=latency_ms
        )
        
        # Create response
        response = ConvoTurnResponse(
            reply=ai_reply,
            turn=turn
        )
        
        return response, 200
        
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def summarize_convo_post(body):  # noqa: E501
    """Summarize conversation for personalization/cost control (backlog)

     # noqa: E501

    :param summarize_request: 
    :type summarize_request: dict | bytes

    :rtype: Union[Summary, Tuple[Summary, int], Tuple[Summary, int, Dict[str, str]]
    """
    summarize_request = body
    if connexion.request.is_json:
        summarize_request = SummarizeRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
