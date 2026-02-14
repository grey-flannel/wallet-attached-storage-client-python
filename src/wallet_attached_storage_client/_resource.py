from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from wallet_attached_storage_client._http_signature import create_authorization_header
from wallet_attached_storage_client._types import StorageResponse

if TYPE_CHECKING:
    from wallet_attached_storage_client._types import Signer


class Resource:
    """A resource within a WAS space, supporting GET/PUT/POST/DELETE."""

    def __init__(
        self,
        *,
        client: httpx.Client,
        path: str,
        signer: Signer | None = None,
    ) -> None:
        self._client = client
        self._path = path
        self._signer = signer

    @property
    def path(self) -> str:
        return self._path

    def _make_headers(
        self,
        method: str,
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, str]:
        merged: dict[str, str] = {}
        if headers:
            merged.update(headers)
        effective_signer = signer or self._signer
        if effective_signer:
            auth = create_authorization_header(
                signer=effective_signer,
                method=method,
                url=self._path,
            )
            merged["authorization"] = auth
        return merged

    def get(
        self,
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> StorageResponse:
        h = self._make_headers("GET", signer=signer, headers=headers)
        resp = self._client.get(self._path, headers=h)
        return StorageResponse(resp)

    def put(
        self,
        content: bytes = b"",
        content_type: str = "application/octet-stream",
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> StorageResponse:
        h = self._make_headers("PUT", signer=signer, headers=headers)
        h.setdefault("content-type", content_type)
        resp = self._client.put(self._path, content=content, headers=h)
        return StorageResponse(resp)

    def post(
        self,
        content: bytes = b"",
        content_type: str = "application/octet-stream",
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> StorageResponse:
        h = self._make_headers("POST", signer=signer, headers=headers)
        h.setdefault("content-type", content_type)
        resp = self._client.post(self._path, content=content, headers=h)
        return StorageResponse(resp)

    def delete(
        self,
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> StorageResponse:
        h = self._make_headers("DELETE", signer=signer, headers=headers)
        resp = self._client.delete(self._path, headers=h)
        return StorageResponse(resp)
