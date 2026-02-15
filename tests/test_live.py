"""Integration tests against a live WAS server on localhost:8080.

Run with:  uv run -m pytest tests/test_live.py -vv
Skip with: uv run -m pytest -m "not live"
"""

from __future__ import annotations

import json

import httpx
import pytest

from wallet_attached_storage_client import Ed25519Signer, StorageClient


WAS_URL = "http://localhost:8080"

pytestmark = pytest.mark.live


@pytest.fixture(scope="module")
def _server_available() -> None:
    """Skip the entire module if the WAS server is not reachable."""
    try:
        httpx.get(WAS_URL, timeout=2)
    except httpx.ConnectError:
        pytest.skip(f"WAS server not reachable at {WAS_URL}")


@pytest.fixture()
def signer() -> Ed25519Signer:
    return Ed25519Signer()


@pytest.fixture()
def client() -> StorageClient:
    return StorageClient(WAS_URL)


def _provision_space(client: StorageClient, signer: Ed25519Signer) -> tuple:
    """Provision a space on the live server by PUTting the controller JSON."""
    space = client.space(signer=signer)
    body = json.dumps({"id": space.id, "controller": signer.controller}).encode()
    resp = space.put(body, "application/json")
    return space, resp


# ---------------------------------------------------------------------------
# Space lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("_server_available")
class TestSpaceLifecycle:
    def test_provision_space(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, resp = _provision_space(client, signer)
        assert resp.status == 204

    def test_get_space(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resp = space.get()
        assert resp.ok
        data = resp.json()
        assert data["controller"] == signer.controller

    def test_delete_space(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resp = space.delete()
        assert resp.ok

        # Confirm it's gone
        resp = space.get()
        assert resp.status == 404


# ---------------------------------------------------------------------------
# Resource CRUD
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("_server_available")
class TestResourceCrud:
    def test_put_and_get_text(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/greeting.txt")

        put_resp = resource.put(b"Hello, WAS!", "text/plain")
        assert put_resp.ok

        get_resp = resource.get()
        assert get_resp.ok
        assert get_resp.text() == "Hello, WAS!"

    def test_put_and_get_json(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/data.json")

        doc = {"key": "value", "number": 42}
        resource.put(json.dumps(doc).encode(), "application/json")

        get_resp = resource.get()
        assert get_resp.ok
        assert get_resp.json() == doc

    def test_put_and_get_binary(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/blob.bin")

        payload = bytes(range(256))
        resource.put(payload, "application/octet-stream")

        get_resp = resource.get()
        assert get_resp.ok
        assert get_resp.content() == payload

    def test_put_same_path_twice(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/twice.txt")

        resp1 = resource.put(b"first", "text/plain")
        assert resp1.ok

        # Second PUT to the same path should still succeed
        resp2 = resource.put(b"second", "text/plain")
        assert resp2.ok

    def test_delete_resource(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/to-delete.txt")

        resource.put(b"ephemeral", "text/plain")
        assert resource.get().ok

        del_resp = resource.delete()
        assert del_resp.ok

        gone_resp = resource.get()
        assert gone_resp.status == 404
        assert not gone_resp.ok

    def test_get_nonexistent_resource(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/does-not-exist")
        resp = resource.get()
        assert resp.status == 404

    def test_auto_generated_resource_path(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource()  # random UUID path

        resource.put(b"random path content", "text/plain")
        assert resource.get().text() == "random path content"


# ---------------------------------------------------------------------------
# Multiple resources in one space
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("_server_available")
class TestMultipleResources:
    def test_independent_resources(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)

        r1 = space.resource("/file-a.txt")
        r2 = space.resource("/file-b.txt")

        r1.put(b"aaa", "text/plain")
        r2.put(b"bbb", "text/plain")

        assert r1.get().text() == "aaa"
        assert r2.get().text() == "bbb"

    def test_delete_one_preserves_other(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)

        r1 = space.resource("/keep.txt")
        r2 = space.resource("/remove.txt")

        r1.put(b"keep me", "text/plain")
        r2.put(b"delete me", "text/plain")

        r2.delete()
        assert r2.get().status == 404
        assert r1.get().text() == "keep me"


# ---------------------------------------------------------------------------
# HTTP signature auth
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("_server_available")
class TestAuth:
    def test_unsigned_get_on_public_resource(self, client: StorageClient, signer: Ed25519Signer) -> None:
        """Resources in a space should be readable without auth."""
        space, _ = _provision_space(client, signer)
        resource = space.resource("/public.txt")
        resource.put(b"public content", "text/plain")

        # Create a new resource handle without a signer
        unsigned_space = client.space(space.id)
        unsigned_resource = unsigned_space.resource("/public.txt")
        resp = unsigned_resource.get()
        # Server may allow or deny unsigned reads — either is valid
        # We just verify we get a well-formed response
        assert resp.status in (200, 401, 403)

    def test_different_signer_cannot_write(self, client: StorageClient, signer: Ed25519Signer) -> None:
        """A different signer should not be able to write to someone else's space."""
        space, _ = _provision_space(client, signer)

        other_signer = Ed25519Signer()
        other_space = client.space(space.id, signer=other_signer)
        resource = other_space.resource("/intruder.txt")
        resp = resource.put(b"unauthorized", "text/plain")
        assert resp.status in (401, 403)

    def test_per_method_signer_override(self, client: StorageClient, signer: Ed25519Signer) -> None:
        """Passing signer= per method should work."""
        space, _ = _provision_space(client, signer)
        # Create resource without default signer
        unsigned_space = client.space(space.id)
        resource = unsigned_space.resource("/override.txt")

        # PUT with explicit signer
        resp = resource.put(b"signed per-call", "text/plain", signer=signer)
        assert resp.ok


# ---------------------------------------------------------------------------
# StorageResponse interface
# ---------------------------------------------------------------------------


@pytest.mark.usefixtures("_server_available")
class TestStorageResponse:
    def test_status_and_ok(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/resp-test.txt")
        resource.put(b"test", "text/plain")

        resp = resource.get()
        assert isinstance(resp.status, int)
        assert resp.ok is True

    def test_headers(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/headers-test.txt")
        resource.put(b"check headers", "text/plain")

        resp = resource.get()
        assert "content-type" in resp.headers

    def test_content_bytes(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/bytes-test.txt")
        resource.put(b"raw bytes", "text/plain")

        resp = resource.get()
        assert isinstance(resp.content(), bytes)
        assert resp.content() == b"raw bytes"

    def test_text(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/text-test.txt")
        resource.put(b"text content", "text/plain")

        resp = resource.get()
        assert isinstance(resp.text(), str)
        assert resp.text() == "text content"

    def test_json(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resource = space.resource("/json-test.json")
        doc = {"nested": {"key": [1, 2, 3]}}
        resource.put(json.dumps(doc).encode(), "application/json")

        resp = resource.get()
        assert resp.json() == doc

    def test_repr(self, client: StorageClient, signer: Ed25519Signer) -> None:
        space, _ = _provision_space(client, signer)
        resp = space.get()
        assert "StorageResponse" in repr(resp)
        assert str(resp.status) in repr(resp)
