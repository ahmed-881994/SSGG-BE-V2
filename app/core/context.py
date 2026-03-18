"""Request context management using contextvars for async-safe storage"""
from contextvars import ContextVar
from typing import Optional

# Context variable to store request_id across async calls
request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
user_id_var: ContextVar[Optional[int]] = ContextVar('user_id', default=None)


def set_request_id(request_id: str) -> None:
    """Set the request_id in the current context"""
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Get the request_id from the current context"""
    return request_id_var.get()


def set_user_id(user_id: int) -> None:
    """Set the user_id in the current context"""
    user_id_var.set(user_id)


def get_user_id() -> Optional[int]:
    """Get the user_id from the current context"""
    return user_id_var.get()


def clear_context() -> None:
    """Clear all context variables (called after request completion)"""
    request_id_var.set(None)
    user_id_var.set(None)
