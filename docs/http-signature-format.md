# HTTP Signature Format (Cavage Draft-12 with Digital Bazaar Extension)

This document describes the exact HTTP Signature wire format used by the
Wallet Attached Storage client, based on
[draft-cavage-http-signatures-12](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-12)
with a Digital Bazaar extension (`(key-id)` pseudo-header). This is the format
a WAS server must be able to verify.

The WAS spec says servers MUST support RFC 9421 and MAY support Cavage
draft-12. This client implements Cavage draft-12 because that is what the
reference JS implementation (`@wallet.storage/fetch-client`) uses.

## Authorization Header

Every authenticated request carries an `Authorization` header with the
`Signature` scheme:

```http
Authorization: Signature keyId="<key-id>",headers="<headers>",signature="<sig>",created="<ts>",expires="<ts>"
```

### Parameters

| Parameter   | Value                                                             | Example                                         |
| ----------- | ----------------------------------------------------------------- | ----------------------------------------------- |
| `keyId`     | The signer's DID Key verification method ID                       | `did:key:z6Mk...#z6Mk...`                       |
| `headers`   | Space-separated list of signed pseudo-headers                     | `(created) (expires) (key-id) (request-target)` |
| `signature` | URL-safe base64 of the raw signature bytes, **no padding**        | `abcDEF123...`                                  |
| `created`   | Unix epoch seconds (integer) when the signature was created       | `1700000000`                                    |
| `expires`   | Unix epoch seconds (integer) when the signature expires           | `1700000030`                                    |

Notes:

- `created` and `expires` are quoted as strings in the header but represent integer timestamps.
- The default expiration window is **30 seconds** after creation.
- The `algorithm` parameter from the draft is omitted; the algorithm is
  implicit from the key type (Ed25519).

### Concrete Example

```http
Authorization: Signature keyId="did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK#z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK",headers="(created) (expires) (key-id) (request-target)",signature="abc123...",created="1700000000",expires="1700000030"
```

## Signature String Construction

The signature is computed over a plaintext string built from pseudo-headers.
Each pseudo-header produces one `name: value` line. Lines are joined with `\n`
(no trailing newline).

### Default Pseudo-Headers (in order)

| Pseudo-Header      | Value                                                                                     |
| ------------------ | ----------------------------------------------------------------------------------------- |
| `(created)`        | The `created` timestamp as a decimal string                                               |
| `(expires)`        | The `expires` timestamp as a decimal string                                               |
| `(key-id)`         | The `keyId` value (DID Key verification method ID) — **Digital Bazaar extension**         |
| `(request-target)` | Lowercased HTTP method + space + request path (e.g. `get /space/abc-123/my-resource`)     |

### Example Signature String

For a `GET /space/abc-123/my-resource` with `created=1700000000`,
`expires=1700000030`, `keyId=did:key:test`:

```text
(created): 1700000000
(expires): 1700000030
(key-id): did:key:test
(request-target): get /space/abc-123/my-resource
```

This plaintext string is UTF-8 encoded and then signed.

## Signing Algorithm

- **Key type**: Ed25519 (identified via `did:key` with multicodec prefix `0xed01`)
- **Signature**: Raw Ed25519 signature (64 bytes)
- **Encoding**: URL-safe base64 (`base64.urlsafe_b64encode`), trailing `=` padding stripped

## DID Key Format

The `keyId` is a `did:key` verification method ID constructed as:

```text
did:key:<fingerprint>#<fingerprint>
```

Where `<fingerprint>` is:

```text
z + base58btc( 0xed01 || raw_public_key_bytes )
```

- `0xed01` is the two-byte multicodec prefix for Ed25519 public keys.
- `base58btc` is Bitcoin-style base58 encoding (alphabet: `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`).
- The `z` prefix indicates base58btc encoding per the Multibase spec.

Example: `did:key:z6MkhaXgBZDvotDkL5257faiztiGiC2QtKLGpbnnEGta2doK`

## Server Verification Steps

To verify an incoming request, a server should:

1. Parse the `Authorization` header to extract `keyId`, `headers`, `signature`,
   `created`, and `expires`.
2. Check that `expires` has not passed (reject with 401 if stale).
3. Extract the raw public key bytes from the `keyId` DID:
   - Strip the `did:key:` prefix and `#fragment`.
   - Strip the leading `z` (multibase prefix).
   - Base58-decode the remainder.
   - Strip the first two bytes (`0xed01` multicodec prefix).
   - The remaining 32 bytes are the Ed25519 public key.
4. Reconstruct the signature string using the `headers` list, the parsed
   timestamps, the `keyId`, and the request method + path.
5. URL-safe base64 decode the `signature` value (re-add padding as needed).
6. Verify the Ed25519 signature over the UTF-8 encoded signature string.

## Differences from Stock Cavage Draft-12

| Aspect                       | Cavage Draft-12                | This Implementation                           |
| ---------------------------- | ------------------------------ | --------------------------------------------- |
| `(key-id)` pseudo-header     | Not in the draft               | Added by Digital Bazaar; included by default  |
| `algorithm` parameter        | Recommended                    | Omitted; inferred from key type               |
| `keyId` format               | Opaque string                  | Always a `did:key` verification method ID     |
| Signature encoding           | Standard base64 (RFC 4648 \$4) | URL-safe base64, no padding                   |
| Real HTTP headers            | Supported                      | Not used; only pseudo-headers are signed      |
