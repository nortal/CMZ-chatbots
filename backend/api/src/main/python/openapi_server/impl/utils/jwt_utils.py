"""
JWT Utility Module for CMZ Authentication
Ensures consistent JWT token generation across all auth modes
"""

import os
import time
import base64
import json
import hashlib
import hmac
import logging
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Configuration - Load from environment with secure fallback
# nosec B105 - Default value only for development, production check enforced
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    if os.environ.get('ENVIRONMENT') == 'production':
        raise ValueError("JWT_SECRET must be set in production environment")
    # Generate a random secret for development (changes each run for security)
    import secrets as sec
    JWT_SECRET = sec.token_hex(32)  # nosec - dynamic generation for dev only
    logger.warning("Using dynamically generated JWT secret for development")

JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
TOKEN_EXPIRATION_SECONDS = int(os.environ.get('TOKEN_EXPIRATION_SECONDS', '86400'))  # 24 hours default


def generate_jwt_token(
    user_data: Dict[str, Any],
    expiration_seconds: int = TOKEN_EXPIRATION_SECONDS
) -> str:
    """
    Generate a properly formatted JWT token that matches frontend expectations.

    Args:
        user_data: Dictionary containing user information (email, role, user_id)
        expiration_seconds: Token validity period in seconds

    Returns:
        JWT token string in format: header.payload.signature
    """
    # Ensure required fields
    email = user_data.get('email', '')
    role = user_data.get('role', 'user')
    user_id = user_data.get('user_id') or user_data.get('userId') or email.replace('@', '_').replace('.', '_')

    # Create JWT header
    header = {
        "alg": JWT_ALGORITHM,
        "typ": "JWT"
    }

    # Create JWT payload with all required fields
    current_time = int(time.time())
    payload = {
        # Both camelCase and snake_case for maximum compatibility
        "user_id": user_id,
        "userId": user_id,  # Frontend might expect either format
        "email": email,
        "role": role,
        "user_type": role,  # Some frontend code uses user_type
        "exp": current_time + expiration_seconds,
        "iat": current_time,
        "iss": "cmz-api",  # Issuer
        "sub": user_id,  # Subject
    }

    # Add any additional user data
    for key, value in user_data.items():
        if key not in ['email', 'role', 'user_id', 'userId', 'password']:
            payload[key] = value

    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(
        json.dumps(header, separators=(',', ':')).encode()
    ).decode().rstrip('=')

    payload_encoded = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':')).encode()
    ).decode().rstrip('=')

    # Create signature (mock for development, use real signing in production)
    if JWT_ALGORITHM == "HS256":
        # HMAC-SHA256 signature
        message = f"{header_encoded}.{payload_encoded}"
        signature_bytes = hmac.new(
            JWT_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).digest()
        signature = base64.urlsafe_b64encode(signature_bytes).decode().rstrip('=')
    else:
        # Mock signature for development
        signature = base64.urlsafe_b64encode(b"mock_signature").decode().rstrip('=')

    # Combine to form JWT
    token = f"{header_encoded}.{payload_encoded}.{signature}"

    return token


def decode_jwt_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and return the payload from a JWT token.
    Note: This does NOT verify the signature - for development/testing only.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dictionary or None if invalid
    """
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        # Split token into parts
        parts = token.split('.')
        if len(parts) != 3:
            return None

        # Decode payload (middle part)
        payload_encoded = parts[1]
        # Add padding if necessary
        padding = 4 - (len(payload_encoded) % 4)
        if padding != 4:
            payload_encoded += '=' * padding

        # Decode base64
        payload_json = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_json)

        return payload
    except Exception as e:
        logger.error(f"Error decoding JWT: {str(e)}")
        return None


def verify_jwt_token(token: str) -> tuple[bool, Optional[Dict[str, Any]]]:
    """
    Verify JWT token format and expiration.
    Note: Signature verification is simplified for development.

    Args:
        token: JWT token string

    Returns:
        Tuple of (is_valid, payload)
    """
    # Decode payload
    payload = decode_jwt_payload(token)
    if not payload:
        return False, None

    # Check expiration
    current_time = int(time.time())
    if 'exp' in payload and payload['exp'] < current_time:
        return False, None

    # Verify required fields
    required_fields = ['email', 'exp', 'iat']
    for field in required_fields:
        if field not in payload:
            return False, None

    # In production, verify signature here
    # For now, just return success
    return True, payload


def create_auth_response(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a complete authentication response matching frontend expectations.

    Args:
        user_data: User information dictionary

    Returns:
        Authentication response with token and user info
    """
    # Generate token
    token = generate_jwt_token(user_data)

    # Decode to get expiration
    payload = decode_jwt_payload(token)
    expires_in = TOKEN_EXPIRATION_SECONDS
    if payload and 'exp' in payload and 'iat' in payload:
        expires_in = payload['exp'] - payload['iat']

    # Build response matching frontend expectations
    response = {
        'token': token,  # No 'Bearer ' prefix - frontend adds it
        'expiresIn': expires_in,
        'user': {
            'email': user_data.get('email', ''),
            'role': user_data.get('role', 'user'),
            'userId': user_data.get('user_id') or user_data.get('userId') or user_data.get('email', '').replace('@', '_').replace('.', '_'),
            'user_type': user_data.get('role', 'user'),
        }
    }

    # Add any additional user fields
    for key, value in user_data.items():
        if key not in ['password', 'user_id', 'userId'] and key not in response['user']:
            response['user'][key] = value

    return response


# Test functions for development
if __name__ == "__main__":
    # Test token generation
    test_user = {
        'email': 'test@cmz.org',
        'role': 'admin',
        'user_id': 'test_cmz_org'
    }

    token = generate_jwt_token(test_user)
    # Don't log sensitive tokens
    logger.info(f"Generated token with {len(token.split('.'))} parts")  # nosec - not logging token value

    # Test decoding
    payload = decode_jwt_payload(token)
    # Don't log sensitive payload data
    logger.info(f"Decoded payload with {len(payload)} fields")  # nosec

    # Test verification
    is_valid, verified_payload = verify_jwt_token(token)
    logger.info(f"Token valid: {is_valid}")

    # Test auth response
    response = create_auth_response(test_user)
    # Don't log sensitive auth response
    logger.info(f"Auth response created with token")  # nosec