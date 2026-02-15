import uuid

import pytest

from wallet_attached_storage_client._urn_uuid import is_urn_uuid, make_urn_uuid, parse_urn_uuid


class TestIsUrnUuid:
    def test_valid(self) -> None:
        assert is_urn_uuid("urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479")

    def test_valid_uppercase(self) -> None:
        assert is_urn_uuid("urn:uuid:F47AC10B-58CC-4372-A567-0E02B2C3D479")

    def test_missing_prefix(self) -> None:
        assert not is_urn_uuid("f47ac10b-58cc-4372-a567-0e02b2c3d479")

    def test_wrong_prefix(self) -> None:
        assert not is_urn_uuid("urn:oid:f47ac10b-58cc-4372-a567-0e02b2c3d479")

    def test_empty(self) -> None:
        assert not is_urn_uuid("")

    def test_truncated(self) -> None:
        assert not is_urn_uuid("urn:uuid:f47ac10b-58cc-4372")

    def test_extra_chars(self) -> None:
        assert not is_urn_uuid("urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479x")


class TestParseUrnUuid:
    def test_roundtrip(self) -> None:
        urn = "urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479"
        result = parse_urn_uuid(urn)
        assert isinstance(result, uuid.UUID)
        assert str(result) == "f47ac10b-58cc-4372-a567-0e02b2c3d479"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_urn_uuid("not-a-urn")


class TestMakeUrnUuid:
    def test_random(self) -> None:
        urn = make_urn_uuid()
        assert is_urn_uuid(urn)

    def test_from_uuid(self) -> None:
        u = uuid.UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479")
        urn = make_urn_uuid(u)
        assert urn == "urn:uuid:f47ac10b-58cc-4372-a567-0e02b2c3d479"

    def test_unique(self) -> None:
        assert make_urn_uuid() != make_urn_uuid()
