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
    headers = include_headers or _DEFAULT_INCLUDE_HEADERS
    parts: list[str] = []
    for h in headers:
        if h == "(created)":
            parts.append(f"(created): {created}")
        elif h == "(expires)":
            parts.append(f"(expires): {expires}")
        elif h == "(key-id)":
            parts.append(f"(key-id): {key_id}")
        elif h == "(request-target)":
            parts.append(f"(request-target): {method.lower()} {path}")
        else:
            raise ValueError(f"Unsupported pseudo-header: {h!r}")
    return "\n".join(parts)


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
        signature="<base64>",created=N,expires=N

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
    sig_b64 = base64.b64encode(sig_bytes).decode("ascii")

    headers_param = " ".join(headers)
    return (
        f'Signature keyId="{key_id}",'
        f'headers="{headers_param}",'
        f'signature="{sig_b64}",'
        f"created={created_ts},"
        f"expires={expires_ts}"
    )
