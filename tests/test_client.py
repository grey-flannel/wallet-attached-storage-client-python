from wallet_attached_storage_client._client import StorageClient
from wallet_attached_storage_client._space import Space
from wallet_attached_storage_client._urn_uuid import is_urn_uuid

from .conftest import Ed25519TestSigner


class TestStorageClient:
    def test_space_with_id(self, mock_client: StorageClient, space_id: str) -> None:
        s = mock_client.space(space_id)
        assert isinstance(s, Space)
        assert s.id == space_id

    def test_space_generates_id(self, mock_client: StorageClient) -> None:
        s = mock_client.space()
        assert is_urn_uuid(s.id)

    def test_space_with_signer(self, mock_client: StorageClient, signer: Ed25519TestSigner) -> None:
        s = mock_client.space(signer=signer)
        assert is_urn_uuid(s.id)

    def test_context_manager(self) -> None:
        with StorageClient("https://example.com") as client:
            assert client is not None

    def test_close_only_owned_client(self, mock_client: StorageClient) -> None:
        # mock_client was given an external httpx_client, so close() should not close it
        mock_client.close()
        # The underlying httpx client should still be usable
        s = mock_client.space()
        assert is_urn_uuid(s.id)
