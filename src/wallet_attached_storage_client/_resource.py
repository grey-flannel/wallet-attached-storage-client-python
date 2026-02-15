from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from wallet_attached_storage_client._http_signature import build_auth_headers

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

    def _auth_headers(
        self, method: str, *, signer: Signer | None = None, headers: dict[str, str] | None = None
    ) -> dict[str, str]:
        return build_auth_headers(method=method, path=self._path, signer=signer or self._signer, headers=headers)

    def get(
        self,
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        h = self._auth_headers("GET", signer=signer, headers=headers)
        return self._client.get(self._path, headers=h)

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
        return self._client.put(self._path, content=content, headers=h)

    def post(
        self,
        content: bytes = b"",
        content_type: str = "application/octet-stream",
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        h = self._auth_headers("POST", signer=signer, headers=headers)
        h.setdefault("content-type", content_type)
        return self._client.post(self._path, content=content, headers=h)

    def delete(
        self,
        *,
        signer: Signer | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        h = self._auth_headers("DELETE", signer=signer, headers=headers)
        return self._client.delete(self._path, headers=h)
