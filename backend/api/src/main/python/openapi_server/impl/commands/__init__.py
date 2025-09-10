"""
Commands package for hexagonal architecture implementation.

This package contains command handlers that implement core business logic
independent of infrastructure concerns. Commands can be invoked from:
- Flask API endpoints
- AWS Lambda functions  
- Background jobs
- CLI tools

Following SOLID principles:
- Single Responsibility: Each command handles one business operation
- Open/Closed: Commands are extensible without modification
- Dependency Inversion: Commands depend on abstractions, not concretions
"""

from .cascade_delete import execute_cascade_delete, CascadeDeleteCommand, CascadeDeleteProcessor

__all__ = [
    'execute_cascade_delete',
    'CascadeDeleteCommand', 
    'CascadeDeleteProcessor'
]