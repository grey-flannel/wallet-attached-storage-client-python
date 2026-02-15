"""Cavage draft-12 HTTP Signature construction with Digital Bazaar (key-id) extension.

Matches the JS ``authorization-signature`` library used by @wallet.storage/fetch-client.
Signs pseudo-headers: (created), (expires), (key-id), (request-target).
"""

from __future__ import annotations

import base64
import math
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wallet_attached_storage_client._types import Signer

_DEFAULT_INCLUDE_HEADERS = [
    "(created)",
    "(expires)",
    "(key-id)",
    "(request-target)",
]

_EXPIRATION_SECONDS = 30


def build_signature_string(
    *,
    method: str,
    path: str,
    created: int,
    expires: int,
    key_id: str,
    include_headers: list[str] | None = None,
) -> str:
    """Build the plaintext string to be signed per Cavage draft-12.

    Each pseudo-header produces one ``name: value`` line; lines are joined with ``\\n``.
    """
    values = {
        "(created)": str(created),
        "(expires)": str(expires),
        "(key-id)": key_id,
        "(request-target)": f"{method.lower()} {path}",
    }
    headers = include_headers or _DEFAULT_INCLUDE_HEADERS
    parts: list[str] = []
    for h in headers:
        if h not in values:
            raise ValueError(f"Unsupported pseudo-header: {h!r}")
        parts.append(f"{h}: {values[h]}")
    return "\n".join(parts)


def build_auth_headers(
    *,
    method: str,
    path: str,
    signer: Signer | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, str]:
    """Merge caller-supplied *headers* with an ``Authorization`` header when a *signer* is present."""
    merged: dict[str, str] = {}
    if headers:
        merged.update(headers)
    if signer:
        merged["authorization"] = create_authorization_header(signer=signer, method=method, url=path)
    return merged


def create_authorization_header(
    *,
    signer: Signer,
    method: str,
    url: str,
    created: float | None = None,
    expires: float | None = None,
    include_headers: list[str] | None = None,
) -> str:
    """Create a full ``Authorization`` header value using HTTP Signatures (Cavage draft-12).

    Returns a string like::

        Signature keyId="did:key:...",headers="(created) (expires) (key-id) (request-target)",
        signature="<base64>",created="N",expires="N"

    The *signer* must implement the ``Signer`` protocol (``id`` property, ``sign(data)`` method).
    """
    now = time.time()
    created_ts = math.floor(created if created is not None else now)
    expires_ts = math.floor(expires if expires is not None else now + _EXPIRATION_SECONDS)

    headers = include_headers or _DEFAULT_INCLUDE_HEADERS
    key_id = signer.id

    sig_string = build_signature_string(
        method=method,
        path=url,
        created=created_ts,
        expires=expires_ts,
        key_id=key_id,
        include_headers=headers,
    )

    sig_bytes = signer.sign(sig_string.encode("utf-8"))
    sig_b64 = base64.urlsafe_b64encode(sig_bytes).decode("ascii").rstrip("=")

    headers_param = " ".join(headers)
    return (
        f'Signature keyId="{key_id}",'
        f'headers="{headers_param}",'
        f'signature="{sig_b64}",'
        f'created="{created_ts}",'
        f'expires="{expires_ts}"'
    )
