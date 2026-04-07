from typing import Optional


class SSGGApiError(Exception):
    """base exception class"""

    def __init__(self, message: str = "Service is unavailable", name: Optional[str] = "SSGGApiError"):
        """
        Args:
            message (str): Error message to be displayed.
            name (str): Name of the error.
        """
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)
        
        
class ServiceError(SSGGApiError):
    """failures in external services or APIs, like a database or a third-party service"""

    pass


class EntityDoesNotExistError(SSGGApiError):
    """database returns nothing"""

    pass


class EntityAlreadyExistsError(SSGGApiError):
    """conflict detected, like trying to create a resource that already exists"""

    pass


class InvalidOperationError(SSGGApiError):
    """invalid operations like trying to delete a non-existing entity, etc."""

    pass


class AuthenticationFailed(SSGGApiError):
    """invalid authentication credentials"""

    pass


class InvalidTokenError(SSGGApiError):
    """invalid token"""

    pass

class AuthorizationError(SSGGApiError):
    """insufficient permissions or forbidden access"""

    pass