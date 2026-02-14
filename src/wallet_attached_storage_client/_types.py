from __future__ import annotations

from typing import Any, NewType, Protocol, runtime_checkable

import httpx


UrnUuid = NewType("UrnUuid", str)


@runtime_checkable
class Signer(Protocol):
    @property
    def id(self) -> str: ...

    def sign(self, data: bytes) -> bytes: ...


class StorageResponse:
    """Thin wrapper around httpx.Response exposing a stable public API."""

    def __init__(self, response: httpx.Response) -> None:
        self._response = response

    @property
    def status(self) -> int:
        return self._response.status_code

    @property
    def ok(self) -> bool:
        return self._response.is_success

    @property
    def headers(self) -> httpx.Headers:
        return self._response.headers

    def content(self) -> bytes:
        return self._response.content

    def json(self) -> Any:
        return self._response.json()

    def text(self) -> str:
        return self._response.text

    def __repr__(self) -> str:
        return f"StorageResponse(status={self.status})"
