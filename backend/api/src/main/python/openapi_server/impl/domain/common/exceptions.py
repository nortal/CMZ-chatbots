"""Common domain exceptions for authentication system"""


class ValidationError(Exception):
    """Validation error for invalid input"""
    pass


class NotFoundError(Exception):
    """Resource not found error"""
    pass


class ConflictError(Exception):
    """Resource conflict error"""
    pass


class BusinessRuleError(Exception):
    """Business rule violation error"""
    pass


class InvalidStateError(Exception):
    """Invalid state error"""
    pass