"""Domain-specific exceptions for business logic"""


class DomainException(Exception):
    """Base exception for all domain-related errors"""
    pass


class ValidationError(DomainException):
    """Raised when business validation rules are violated"""
    pass


class NotFoundError(DomainException):
    """Raised when a requested entity is not found"""
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} not found: {entity_id}")


class ConflictError(DomainException):
    """Raised when a business operation conflicts with existing state"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnauthorizedError(DomainException):
    """Raised when user lacks permission for requested operation"""
    pass


class BusinessRuleError(DomainException):
    """Raised when a business rule is violated"""
    def __init__(self, rule: str, details: str = ""):
        self.rule = rule
        self.details = details
        super().__init__(f"Business rule violation: {rule}. {details}")


class InvalidStateError(DomainException):
    """Raised when entity is in invalid state for requested operation"""
    def __init__(self, entity_type: str, current_state: str, required_state: str):
        self.entity_type = entity_type
        self.current_state = current_state
        self.required_state = required_state
        super().__init__(f"{entity_type} in invalid state '{current_state}', requires '{required_state}'")