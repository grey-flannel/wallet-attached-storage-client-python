"""End-to-end integration test: create space, write resource, read back, delete, verify 404."""

from wallet_attached_storage_client._client import StorageClient

from .conftest import Ed25519TestSigner


class TestEndToEnd:
    def test_full_lifecycle(self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner) -> None:
        # Create a space
        space = mock_client.space(space_id, signer=signer)

        # Space GET returns a collection
        resp = space.get()
        assert resp.is_success
        assert resp.json()["type"] == "Collection"

        # Create a resource and write data
        resource = space.resource("/document.txt")
        put_resp = resource.put(b"Hello, Wallet Attached Storage!", "text/plain")
        assert put_resp.status_code == 204

        # Read it back
        get_resp = resource.get()
        assert get_resp.is_success
        assert get_resp.status_code == 200
        assert get_resp.text == "Hello, Wallet Attached Storage!"
        assert get_resp.headers["content-type"] == "text/plain"

        # Content bytes also work
        assert get_resp.content == b"Hello, Wallet Attached Storage!"

        # Delete the resource
        del_resp = resource.delete()
        assert del_resp.status_code == 204

        # Verify it's gone
        gone_resp = resource.get()
        assert gone_resp.status_code == 404
        assert not gone_resp.is_success

    def test_multiple_resources_in_space(
        self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner
    ) -> None:
        space = mock_client.space(space_id, signer=signer)

        r1 = space.resource("/file-a")
        r2 = space.resource("/file-b")

        r1.put(b"aaa", "text/plain")
        r2.put(b"bbb", "text/plain")

        assert r1.get().text == "aaa"
        assert r2.get().text == "bbb"

        # Deleting one doesn't affect the other
        r1.delete()
        assert r1.get().status_code == 404
        assert r2.get().text == "bbb"

    def test_post_resource(self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner) -> None:
        space = mock_client.space(space_id, signer=signer)
        resource = space.resource("/items")
        resp = resource.post(b'{"name": "test"}', "application/json")
        assert resp.status_code == 201

    def test_space_delete(self, mock_client: StorageClient, space_id: str, signer: Ed25519TestSigner) -> None:
        space = mock_client.space(space_id, signer=signer)
        resp = space.delete()
        assert resp.status_code == 204
