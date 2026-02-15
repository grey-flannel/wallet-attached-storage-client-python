import pytest

from wallet_attached_storage_client._client import StorageClient
from wallet_attached_storage_client._resource import Resource

from .conftest import Ed25519TestSigner


class TestSpace:
    def test_id_and_path(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        assert s.id == space_id
        assert s.path == "/space/f47ac10b-58cc-4372-a567-0e02b2c3d479"

    def test_invalid_id_raises(self, mock_client: StorageClient) -> None:
        with pytest.raises(ValueError):
            mock_client.space("not-a-urn")

    def test_get(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        resp = s.get()
        assert resp.is_success
        data = resp.json()
        assert data["type"] == "Collection"

    def test_put(self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner) -> None:
        s = mock_client.space(space_id, signer=signer)
        resp = s.put()
        assert resp.status_code == 204

    def test_delete(self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner) -> None:
        s = mock_client.space(space_id, signer=signer)
        resp = s.delete()
        assert resp.status_code == 204

    def test_resource_with_path(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        r = s.resource("/my-resource")
        assert isinstance(r, Resource)
        assert r.path == "/space/f47ac10b-58cc-4372-a567-0e02b2c3d479/my-resource"

    def test_resource_without_leading_slash(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        r = s.resource("data.json")
        assert r.path == "/space/f47ac10b-58cc-4372-a567-0e02b2c3d479/data.json"

    def test_resource_random_path(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        r = s.resource()
        # Should be /space/{uuid}/{random-uuid}
        parts = r.path.split("/")
        assert len(parts) == 4
        assert parts[1] == "space"
        # The last segment should look like a UUID
        assert len(parts[3]) == 36

    def test_signer_propagates_to_resource(
        self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner
    ) -> None:
        s = mock_client.space(space_id, signer=signer)
        r = s.resource("/test")
        # Put should succeed with auth
        resp = r.put(b"hello")
        assert resp.status_code == 204


class TestSpaceSignedRequests:
    def test_get_sends_auth_header(
        self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner
    ) -> None:
        s = mock_client.space(space_id, signer=signer)
        resp = s.get()
        assert resp.is_success
