from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import httpx

from wallet_attached_storage_client._http_signature import build_auth_headers
from wallet_attached_storage_client._resource import Resource
from wallet_attached_storage_client._urn_uuid import is_urn_uuid, parse_urn_uuid

if TYPE_CHECKING:
    from wallet_attached_storage_client._types import Signer


class Space:
    """A WAS storage space identified by a ``urn:uuid``."""

    def __init__(
        self,
        *,
        client: httpx.Client,
        id: str,  # noqa: A002
        signer: Signer | None = None,
    ) -> None:
        if not is_urn_uuid(id):
            raise ValueError(f"Expected a urn:uuid, got {id!r}")
        self._client = client
        self._id = id
        self._uuid = parse_urn_uuid(id)
        self._signer = signer

    @property
    def id(self) -> str:
        return self._id

    @property
    def path(self) -> str:
        return f"/space/{self._uuid}"

    def _auth_headers(
        self, method: str, *, signer: Signer | None = None, headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        return build_auth_headers(method=method, path=self.path, signer=signer or self._signer, headers=headers)

    def get(
        self,
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        h = self._auth_headers("GET", signer=signer, headers=headers)
        return self._client.get(self.path, headers=h)

    def put(
        self,
        content: bytes = b"",
        content_type: str = "application/octet-stream",
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        h = self._auth_headers("PUT", signer=signer, headers=headers)
        h.setdefault("content-type", content_type)
        return self._client.put(self.path, content=content, headers=h)

    def delete(
        self,
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        h = self._auth_headers("DELETE", signer=signer, headers=headers)
        return self._client.delete(self.path, headers=h)

    def resource(
        self,
        path: str | None = None,
        *,
        signer: Signer | None = None,
    ) -> Resource:
        """Create a resource within this space.

        If *path* is ``None``, a random UUID path is generated.
        """
        if path is None:
            path = f"/{uuid.uuid4()}"
        elif not path.startswith("/"):
            path = f"/{path}"
        return Resource(
            client=self._client,
            path=f"{self.path}{path}",
            signer=signer or self._signer,
        )
