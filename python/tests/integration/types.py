"""Integration tests types module."""

from typing import ContextManager, Protocol, TypedDict


class PortForwarder(Protocol):
    """Type stub for the port_forward fixture."""

    def __call__(
        self, *, pod: str, port: int, namespace: str, on_port: int | None = None
    ) -> ContextManager:
        """Create a context where a local port is forwarded to a remote pod."""
        ...


class PortForwardTimeout(Exception):
    pass


class KyuubiCredentials(TypedDict):
    username: str
    password: str
    host: str
