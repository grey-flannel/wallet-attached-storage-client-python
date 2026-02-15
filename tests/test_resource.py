from wallet_attached_storage_client._client import StorageClient

from .conftest import Ed25519TestSigner


class TestResource:
    def test_get_not_found(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        r = s.resource("/nonexistent")
        resp = r.get()
        assert resp.status_code == 404
        assert not resp.is_success

    def test_put_and_get(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        r = s.resource("/my-data")
        put_resp = r.put(b"hello world", "text/plain")
        assert put_resp.status_code == 204

        get_resp = r.get()
        assert get_resp.is_success
        assert get_resp.content == b"hello world"
        assert get_resp.text == "hello world"
        assert get_resp.headers["content-type"] == "text/plain"

    def test_post(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        r = s.resource("/items")
        resp = r.post(b'{"key": "value"}', "application/json")
        assert resp.status_code == 201

    def test_delete(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        r = s.resource("/to-delete")
        r.put(b"data")
        resp = r.delete()
        assert resp.status_code == 204

        # Confirm it's gone
        resp = r.get()
        assert resp.status_code == 404

    def test_path_property(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        r = s.resource("/test-path")
        assert r.path == "/space/f47ac10b-58cc-4372-a567-0e02b2c3d479/test-path"


class TestResourceWithSigner:
    def test_get_with_signer(
        self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner
    ) -> None:
        s = mock_client.space(space_id, signer=signer)
        r = s.resource("/data")
        r.put(b"signed content")
        resp = r.get()
        assert resp.is_success

    def test_put_with_signer(
        self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner
    ) -> None:
        s = mock_client.space(space_id, signer=signer)
        r = s.resource("/data")
        resp = r.put(b"content")
        assert resp.status_code == 204

    def test_delete_with_signer(
        self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner
    ) -> None:
        s = mock_client.space(space_id, signer=signer)
        r = s.resource("/data")
        r.put(b"content")
        resp = r.delete()
        assert resp.status_code == 204

    def test_per_method_signer_override(
        self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner
    ) -> None:
        s = mock_client.space(space_id)  # no default signer
        r = s.resource("/data")
        # Pass signer per-method
        resp = r.put(b"data", signer=signer)
        assert resp.status_code == 204
