from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from wallet_attached_storage_client._signer import Ed25519Signer
from wallet_attached_storage_client._types import Signer


class TestEd25519Signer:
    def test_satisfies_protocol(self) -> None:
        signer = Ed25519Signer()
        assert isinstance(signer, Signer)

    def test_generates_did_key_verification_method_id(self) -> None:
        signer = Ed25519Signer()
        # id is the verification method ID: did:key:z6Mk...#z6Mk...
        assert "#" in signer.id
        did, fragment = signer.id.split("#")
        assert did.startswith("did:key:z6Mk")
        assert fragment.startswith("z6Mk")
        assert did == f"did:key:{fragment}"

    def test_controller(self) -> None:
        signer = Ed25519Signer()
        assert signer.controller.startswith("did:key:z6Mk")
        assert "#" not in signer.controller
        assert signer.id.startswith(signer.controller)

    def test_deterministic_from_key(self) -> None:
        key = Ed25519PrivateKey.generate()
        s1 = Ed25519Signer(key)
        s2 = Ed25519Signer(key)
        assert s1.id == s2.id

    def test_different_keys_different_ids(self) -> None:
        assert Ed25519Signer().id != Ed25519Signer().id

    def test_sign_verifies(self) -> None:
        key = Ed25519PrivateKey.generate()
        signer = Ed25519Signer(key)
        data = b"test payload"
        sig = signer.sign(data)
        assert len(sig) == 64
        # Verify with the public key
        key.public_key().verify(sig, data)

    def test_importable_from_package(self) -> None:
        from wallet_attached_storage_client import Ed25519Signer as Imported
        assert Imported is Ed25519Signer
