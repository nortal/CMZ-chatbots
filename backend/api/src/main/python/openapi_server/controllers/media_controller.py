import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.media import Media  # noqa: E501
from openapi_server import util
from datetime import datetime
import uuid

# In-memory storage for media files (in production, this would be in S3 + DynamoDB)
_media_store = {
    "media_lion_roar": {
        "mediaId": "media_lion_roar",
        "title": "Lion Roar Recording",
        "url": "https://cougarmountainzoo.org/media/lion_roar.mp3",
        "kind": "audio",
        "animalId": "animal_1",
        "created": {"at": "2025-09-11T00:00:00Z", "by": {"userId": "system"}},
        "modified": {"at": "2025-09-11T00:00:00Z", "by": {"userId": "system"}},
        "deleted": None,
        "softDelete": False
    },
    "media_bear_photo": {
        "mediaId": "media_bear_photo",
        "title": "Brown Bear in Habitat",
        "url": "https://cougarmountainzoo.org/media/bear_habitat.jpg",
        "kind": "image",
        "animalId": "animal_2",
        "created": {"at": "2025-09-11T00:00:00Z", "by": {"userId": "system"}},
        "modified": {"at": "2025-09-11T00:00:00Z", "by": {"userId": "system"}},
        "deleted": None,
        "softDelete": False
    }
}

def media_delete(media_id):  # noqa: E501
    """Delete media by id (backlog)

     # noqa: E501

    :param media_id: 
    :type media_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    try:
        if media_id in _media_store:
            # Soft delete - mark as deleted instead of removing
            _media_store[media_id]["softDelete"] = True
            _media_store[media_id]["deleted"] = {
                "at": datetime.utcnow().isoformat() + 'Z', 
                "by": {"userId": "system"}
            }
            return None, 204
        else:
            return Error(code='NOT_FOUND', message=f"Media {media_id} not found"), 404
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def media_get(media_id):  # noqa: E501
    """Fetch media by id (backlog)

     # noqa: E501

    :param media_id: 
    :type media_id: str

    :rtype: Union[Media, Tuple[Media, int], Tuple[Media, int, Dict[str, str]]
    """
    try:
        if media_id in _media_store and not _media_store[media_id].get("softDelete", False):
            media_data = _media_store[media_id].copy()
            return Media.from_dict(media_data)
        else:
            return Error(code='NOT_FOUND', message=f"Media {media_id} not found"), 404
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def upload_media_post(file, title=None, animal_id=None):  # noqa: E501
    """Upload media (image/audio/video) (backlog)

     # noqa: E501

    :param file: 
    :type file: str
    :param title: 
    :type title: str
    :param animal_id: 
    :type animal_id: str

    :rtype: Union[Media, Tuple[Media, int], Tuple[Media, int, Dict[str, str]]
    """
    try:
        # Generate unique media ID
        media_id = f"media_{str(uuid.uuid4()).replace('-', '_')}"
        
        # Simulate file processing and determine media type from filename
        filename = str(file) if file else "unknown.jpg"
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            kind = "image"
        elif filename.lower().endswith(('.mp4', '.mov', '.avi', '.wmv')):
            kind = "video"
        elif filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            kind = "audio"
        else:
            kind = "document"
        
        # Generate a mock URL (in production, this would be S3 URL)
        mock_url = f"https://cougarmountainzoo.org/media/{media_id}/{filename}"
        
        # Create media metadata
        now = datetime.utcnow().isoformat() + 'Z'
        media_data = {
            "mediaId": media_id,
            "title": title or f"Uploaded {kind}",
            "url": mock_url,
            "kind": kind,
            "animalId": animal_id,
            "created": {"at": now, "by": {"userId": "system"}},
            "modified": {"at": now, "by": {"userId": "system"}},
            "deleted": None,
            "softDelete": False
        }
        
        # Store the media metadata
        _media_store[media_id] = media_data
        
        return Media.from_dict(media_data), 201
        
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500
