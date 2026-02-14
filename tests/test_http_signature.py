import base64

import nacl.signing

from wallet_attached_storage_client._http_signature import build_signature_string, create_authorization_header


class Ed25519TestSigner:
    """Test signer using PyNaCl Ed25519."""

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

    def verify(self, data: bytes, signature: bytes) -> bool:
        try:
            self._verify_key.verify(data, signature)
        except nacl.exceptions.BadSignatureError:
            return False
        return True


class TestBuildSignatureString:
    def test_default_headers(self) -> None:
        result = build_signature_string(
            method="GET",
            path="/space/abc-123/my-resource",
            created=1700000000,
            expires=1700000030,
            key_id="did:key:test",
        )
        lines = result.split("\n")
        assert len(lines) == 4
        assert lines[0] == "(created): 1700000000"
        assert lines[1] == "(expires): 1700000030"
        assert lines[2] == "(key-id): did:key:test"
        assert lines[3] == "(request-target): get /space/abc-123/my-resource"

    def test_method_lowercased(self) -> None:
        result = build_signature_string(
            method="PUT",
            path="/space/abc",
            created=0,
            expires=0,
            key_id="k",
        )
        assert "(request-target): put /space/abc" in result

    def test_custom_headers(self) -> None:
        result = build_signature_string(
            method="DELETE",
            path="/x",
            created=1,
            expires=2,
            key_id="k",
            include_headers=["(created)", "(request-target)"],
        )
        lines = result.split("\n")
        assert len(lines) == 2
        assert lines[0] == "(created): 1"
        assert lines[1] == "(request-target): delete /x"

    def test_unsupported_header_raises(self) -> None:
        try:
            build_signature_string(
                method="GET",
                path="/",
                created=0,
                expires=0,
                key_id="k",
                include_headers=["host"],
            )
            assert False, "Expected ValueError"
        except ValueError:
            pass


class TestCreateAuthorizationHeader:
    def test_format(self) -> None:
        signer = Ed25519TestSigner()
        header = create_authorization_header(
            signer=signer,
            method="GET",
            url="/space/abc-123/resource",
            created=1700000000.0,
            expires=1700000030.0,
        )
        assert header.startswith("Signature ")
        assert f'keyId="{signer.id}"' in header
        assert 'headers="(created) (expires) (key-id) (request-target)"' in header
        assert "created=1700000000," in header
        assert "expires=1700000030" in header
        assert 'signature="' in header

    def test_signature_verifies(self) -> None:
        signer = Ed25519TestSigner()
        header = create_authorization_header(
            signer=signer,
            method="PUT",
            url="/space/test-uuid/data",
            created=1700000000.0,
            expires=1700000030.0,
        )
        # Extract signature from header
        sig_start = header.index('signature="') + len('signature="')
        sig_end = header.index('"', sig_start)
        sig_b64 = header[sig_start:sig_end]
        sig_bytes = base64.b64decode(sig_b64)

        # Reconstruct what was signed
        sig_string = build_signature_string(
            method="PUT",
            path="/space/test-uuid/data",
            created=1700000000,
            expires=1700000030,
            key_id=signer.id,
        )
        assert signer.verify(sig_string.encode("utf-8"), sig_bytes)

    def test_default_expiration_window(self) -> None:
        signer = Ed25519TestSigner()
        header = create_authorization_header(
            signer=signer,
            method="GET",
            url="/",
        )
        # Extract created and expires from header
        created_idx = header.index("created=") + len("created=")
        created_end = header.index(",", created_idx)
        created = int(header[created_idx:created_end])

        expires_idx = header.rindex("expires=") + len("expires=")
        expires = int(header[expires_idx:])

        assert expires - created == 30
