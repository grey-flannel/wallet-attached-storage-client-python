from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from wallet_attached_storage_client._space import Space
from wallet_attached_storage_client._types import UrnUuid
from wallet_attached_storage_client._urn_uuid import make_urn_uuid

if TYPE_CHECKING:
    from wallet_attached_storage_client._types import Signer


class StorageClient:
    """Entry-point client for a Wallet Attached Storage server."""

    def __init__(
        self,
        base_url: str,
        *,
        httpx_client: httpx.Client | None = None,
    ) -> None:
        if httpx_client is not None:
            self._client = httpx_client
            self._owns_client = False
        else:
            self._client = httpx.Client(base_url=base_url)
            self._owns_client = True

    def space(
        self,
        id: UrnUuid | str | None = None,  # noqa: A002
        *,
        signer: Signer | None = None,
    ) -> Space:
        """Create a :class:`Space` handle.

        If *id* is ``None``, a new random ``urn:uuid`` is generated.
        """
        if id is None:
            id = make_urn_uuid()  # noqa: A001
        return Space(
            client=self._client,
            id=UrnUuid(id),
            signer=signer,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> StorageClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
