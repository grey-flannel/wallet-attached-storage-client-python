from __future__ import annotations

import base58
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


class Ed25519Signer:
    """Ed25519 signer backed by the ``cryptography`` library.

    Satisfies the :class:`Signer` protocol with a proper ``did:key`` identifier.
    """

    # Multicodec prefix for Ed25519 public keys (0xed 0x01)
    _MULTICODEC_ED25519_PUB = b"\xed\x01"

    def __init__(self, private_key: Ed25519PrivateKey | None = None) -> None:
        self._private_key = private_key or Ed25519PrivateKey.generate()
        pub_bytes = self._private_key.public_key().public_bytes_raw()
        multikey = self._MULTICODEC_ED25519_PUB + pub_bytes
        fingerprint = f"z{base58.b58encode(multikey).decode()}"
        self._controller = f"did:key:{fingerprint}"
        self._id = f"{self._controller}#{fingerprint}"

    @property
    def id(self) -> str:
        """Verification method ID (``did:key:z6Mk...#z6Mk...``)."""
        return self._id

    @property
    def controller(self) -> str:
        """Controller DID (``did:key:z6Mk...``)."""
        return self._controller

    def sign(self, data: bytes) -> bytes:
        return self._private_key.sign(data)
