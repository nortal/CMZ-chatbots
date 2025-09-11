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
import random
import time

# Mock AI responses for different animals based on their personalities
ANIMAL_PERSONALITIES = {
    "animal_1": {  # Lion (Simba)
        "name": "Simba",
        "personality": "Energetic and educational, loves talking about speed and hunting techniques",
        "responses": {
            "greeting": "ROAR! Hello there! I'm Simba, the king of the jungle! Well, technically I live at the zoo now, but I'm still pretty regal. What would you like to know about lions?",
            "hunting": "Ah, hunting! My specialty! We lions are incredible hunters - we work together in groups called prides. The females do most of the hunting while us males protect the territory. We can reach speeds of up to 50 mph in short bursts!",
            "diet": "I'm a carnivore, which means I eat meat! In the wild, we hunt zebras, wildebeest, and buffalo. Here at the zoo, I get specially prepared meals that keep me healthy and strong. Want to know about my favorite foods?",
            "default": "That's an interesting question! As a lion, I love sharing knowledge about big cats, hunting, pride dynamics, and life in the African savanna. What specific aspect of lion life would you like to explore?"
        }
    },
    "animal_2": {  # Bear (Koda)  
        "name": "Koda",
        "personality": "Wise and powerful, enjoys discussing conservation and habitat protection",
        "responses": {
            "greeting": "Hello friend! I'm Koda, a brown bear here at the zoo. I may look cuddly, but I'm actually quite powerful! I love talking about forest conservation and how we can protect wildlife habitats.",
            "hibernation": "Ah, hibernation! It's actually called torpor for us bears. During winter, we slow down our heart rate and breathing, and we don't eat, drink, or eliminate waste. Female bears even give birth to cubs during this time - nature is amazing!",
            "habitat": "Bears need large territories with plenty of food sources - fish, berries, nuts, and sometimes smaller animals. Sadly, habitat loss is a major threat to wild bears. That's why conservation efforts are so important!",
            "default": "That's a thoughtful question! As a bear, I'm passionate about wildlife conservation, forest ecosystems, seasonal behaviors, and how humans can help protect our natural world. What would you like to learn about?"
        }
    }
}

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
            session_id = convo_turn_request.session_id
            context_summary = convo_turn_request.context_summary
        elif hasattr(convo_turn_request, 'to_dict'):
            # Convert to dict and use camelCase keys
            request_data = convo_turn_request.to_dict()
            animal_id = request_data.get('animalId')
            message = request_data.get('message')
            session_id = request_data.get('sessionId')
            context_summary = request_data.get('contextSummary')
        else:
            # Use as dict directly
            request_data = dict(convo_turn_request)
            animal_id = request_data.get('animalId')
            message = request_data.get('message')
            session_id = request_data.get('sessionId')
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
