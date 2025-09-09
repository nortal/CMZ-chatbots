"""
Lambda entry points using hexagonal architecture

These handlers demonstrate how the same business logic can be deployed
as AWS Lambda functions behind API Gateway, using identical domain services
as the Flask application but with Lambda-specific adapters.
"""
from impl.dependency_injection import create_lambda_user_handler

# Initialize Lambda handler (lazy loaded)
_lambda_handler = None


def _get_lambda_handler():
    """Get or create Lambda handler"""
    global _lambda_handler
    if _lambda_handler is None:
        _lambda_handler = create_lambda_user_handler()
    return _lambda_handler


# Lambda entry points for user operations
def lambda_create_user(event, context):
    """
    Lambda handler for POST /users
    
    Event format:
    {
        "body": "{\"email\": \"user@example.com\", \"displayName\": \"User Name\"}",
        "headers": {"Content-Type": "application/json"}
    }
    
    Returns:
    {
        "statusCode": 201,
        "headers": {"Content-Type": "application/json"},
        "body": "{\"userId\": \"...\", \"email\": \"...\", ...}"
    }
    """
    return _get_lambda_handler().create_user(event, context)


def lambda_get_user(event, context):
    """
    Lambda handler for GET /users/{userId}
    
    Event format:
    {
        "pathParameters": {"userId": "123"},
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().get_user(event, context)


def lambda_list_users(event, context):
    """
    Lambda handler for GET /users
    
    Event format:
    {
        "queryStringParameters": {"page": "1", "pageSize": "10"},
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().list_users(event, context)


def lambda_update_user(event, context):
    """
    Lambda handler for PUT /users/{userId}
    
    Event format:
    {
        "pathParameters": {"userId": "123"},
        "body": "{\"displayName\": \"Updated Name\", \"role\": \"admin\"}",
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().update_user(event, context)


def lambda_delete_user(event, context):
    """
    Lambda handler for DELETE /users/{userId}
    
    Event format:
    {
        "pathParameters": {"userId": "123"},
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().delete_user(event, context)


def lambda_create_user_details(event, context):
    """
    Lambda handler for POST /user_details
    
    Event format:
    {
        "body": "{\"userId\": \"123\", \"usage\": {...}}",
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().create_user_details(event, context)


def lambda_get_user_details(event, context):
    """
    Lambda handler for GET /user_details/{userId}
    
    Event format:
    {
        "pathParameters": {"userId": "123"},
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().get_user_details(event, context)


def lambda_list_user_details(event, context):
    """
    Lambda handler for GET /user_details
    
    Event format:
    {
        "queryStringParameters": {"page": "1", "pageSize": "10"},
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().list_user_details(event, context)


def lambda_update_user_details(event, context):
    """
    Lambda handler for PUT /user_details/{userId}
    
    Event format:
    {
        "pathParameters": {"userId": "123"},
        "body": "{\"usage\": {\"totalSessions\": 10}}",
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().update_user_details(event, context)


def lambda_delete_user_details(event, context):
    """
    Lambda handler for DELETE /user_details/{userId}
    
    Event format:
    {
        "pathParameters": {"userId": "123"},
        "headers": {"Content-Type": "application/json"}
    }
    """
    return _get_lambda_handler().delete_user_details(event, context)


# Example usage and testing functions
def test_lambda_locally():
    """
    Test Lambda functions locally with sample events
    This can be used for local testing and development
    """
    import json
    
    # Sample create user event
    create_event = {
        "body": json.dumps({
            "email": "test@example.com",
            "displayName": "Test User",
            "role": "user",
            "userType": "parent"
        }),
        "headers": {"Content-Type": "application/json"}
    }
    
    # Test create user
    print("Testing lambda_create_user...")
    result = lambda_create_user(create_event, None)
    print(f"Create result: {result}")
    
    # Extract userId from result for further testing
    if result["statusCode"] == 201:
        user_data = json.loads(result["body"])
        user_id = user_data["userId"]
        
        # Sample get user event
        get_event = {
            "pathParameters": {"userId": user_id},
            "headers": {"Content-Type": "application/json"}
        }
        
        # Test get user
        print(f"\nTesting lambda_get_user for userId={user_id}...")
        result = lambda_get_user(get_event, None)
        print(f"Get result: {result}")
        
        # Test list users
        list_event = {
            "queryStringParameters": {"page": "1", "pageSize": "10"},
            "headers": {"Content-Type": "application/json"}
        }
        
        print("\nTesting lambda_list_users...")
        result = lambda_list_users(list_event, None)
        print(f"List result: {result}")


# CloudFormation/SAM template helpers
def get_lambda_function_configurations():
    """
    Return Lambda function configurations for CloudFormation/SAM templates
    
    This helps generate the infrastructure as code for deploying
    the Lambda functions with proper API Gateway integration.
    """
    return {
        "CreateUser": {
            "handler": "lambda_handlers.lambda_create_user",
            "events": [
                {
                    "type": "api",
                    "properties": {
                        "path": "/users",
                        "method": "post"
                    }
                }
            ]
        },
        "GetUser": {
            "handler": "lambda_handlers.lambda_get_user", 
            "events": [
                {
                    "type": "api",
                    "properties": {
                        "path": "/users/{userId}",
                        "method": "get"
                    }
                }
            ]
        },
        "ListUsers": {
            "handler": "lambda_handlers.lambda_list_users",
            "events": [
                {
                    "type": "api", 
                    "properties": {
                        "path": "/users",
                        "method": "get"
                    }
                }
            ]
        },
        "UpdateUser": {
            "handler": "lambda_handlers.lambda_update_user",
            "events": [
                {
                    "type": "api",
                    "properties": {
                        "path": "/users/{userId}",
                        "method": "put"
                    }
                }
            ]
        },
        "DeleteUser": {
            "handler": "lambda_handlers.lambda_delete_user",
            "events": [
                {
                    "type": "api",
                    "properties": {
                        "path": "/users/{userId}",
                        "method": "delete"
                    }
                }
            ]
        }
    }


if __name__ == "__main__":
    # Run local testing when executed directly
    test_lambda_locally()