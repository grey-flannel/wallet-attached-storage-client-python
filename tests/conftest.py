from __future__ import annotations

import base64
import json

import httpx
import nacl.signing
import pytest

from wallet_attached_storage_client._client import StorageClient
from wallet_attached_storage_client._types import UrnUuid


class Ed25519TestSigner:
    """Ed25519 signer backed by PyNaCl, for testing only."""

    def __init__(self) -> None:
        self._signing_key = nacl.signing.SigningKey.generate()
        self._verify_key = self._signing_key.verify_key

    @property
    def id(self) -> str:
        pub_b64 = base64.urlsafe_b64encode(self._verify_key.encode()).decode("ascii").rstrip("=")
        return f"did:key:{pub_b64}"

    def sign(self, data: bytes) -> bytes:
        signed = self._signing_key.sign(data)
        return signed.signature


# In-memory WAS server mock
_store: dict[str, tuple[bytes, str]] = {}


def _mock_handler(request: httpx.Request) -> httpx.Response:
    """Mock httpx transport handler simulating a WAS server."""
    path = request.url.raw_path.decode("utf-8")
    method = request.method

    if method == "PUT":
        body = request.read()
        ct = request.headers.get("content-type", "application/octet-stream")
        _store[path] = (body, ct)
        return httpx.Response(204)

    if method == "POST":
        body = request.read()
        ct = request.headers.get("content-type", "application/octet-stream")
        _store[path] = (body, ct)
        return httpx.Response(201)

    if method == "GET":
        if path in _store:
            body, ct = _store[path]
            return httpx.Response(200, content=body, headers={"content-type": ct})
        # Space GET returns an empty collection
        if path.startswith("/space/") and path.count("/") == 2:
            collection = {"type": "Collection", "totalItems": 0, "items": []}
            return httpx.Response(
                200,
                content=json.dumps(collection).encode(),
                headers={"content-type": "application/activity+json"},
            )
        return httpx.Response(404)

    if method == "DELETE":
        if path in _store:
            del _store[path]
            return httpx.Response(204)
        if path.startswith("/space/") and path.count("/") == 2:
            return httpx.Response(204)
        return httpx.Response(404)

    return httpx.Response(405)


@pytest.fixture(autouse=True)
def _clear_store() -> None:
    _store.clear()


@pytest.fixture()
def signer() -> Ed25519TestSigner:
    return Ed25519TestSigner()


@pytest.fixture()
def mock_client() -> StorageClient:
    transport = httpx.MockTransport(_mock_handler)
    hx = httpx.Client(base_url="https://storage.example", transport=transport)
    return StorageClient("https://storage.example", httpx_client=hx)


@pytest.fixture()
def space_id() -> UrnUuid:
    return UrnUuid("urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479")
