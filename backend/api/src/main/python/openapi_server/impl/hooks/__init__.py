"""
Hooks package for Lambda function integration.

This package contains Lambda function hooks that use the same command
implementations as Flask endpoints, ensuring consistent business logic
across different invocation methods.

Lambda hooks provide:
- Asynchronous processing capabilities
- Event-driven architecture support  
- Scalable background job processing
- External system integration points
"""

from .lambda_cascade_delete import lambda_handler as cascade_delete_handler

__all__ = [
    'cascade_delete_handler'
]