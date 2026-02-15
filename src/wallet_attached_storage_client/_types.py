from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Signer(Protocol):
    @property
    def id(self) -> str: ...

    def sign(self, data: bytes) -> bytes: ...
