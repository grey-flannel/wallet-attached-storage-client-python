# Wallet Attached Storage Client

Python client library for the [Wallet Attached Storage](https://wallet.storage/spec) specification.

## Installation

```bash
pip install wallet-attached-storage-client
```

## Usage

```python
from wallet_attached_storage_client import StorageClient

# Connect to a WAS server
with StorageClient("https://your-was-server.example") as client:
    # Create a space (generates a random urn:uuid if none given)
    space = client.space(signer=your_signer)

    # Write a resource
    resource = space.resource("/my-document.txt")
    resource.put(b"Hello, world!", "text/plain")

    # Read it back
    response = resource.get()
    print(response.text())  # "Hello, world!"

    # Delete it
    resource.delete()
```

### Signer Protocol

The library uses a `Signer` protocol — bring your own Ed25519 implementation (PyNaCl, cryptography, etc.):

```python
class MySigner:
    @property
    def id(self) -> str:
        return "did:key:..."  # your DID key identifier

    def sign(self, data: bytes) -> bytes:
        # sign data with your private key, return raw signature bytes
        ...
```

## API

- **`StorageClient(base_url)`** — entry point; creates `Space` handles
- **`Space`** — represents a WAS space (`get()`, `put()`, `delete()`, `resource()`)
- **`Resource`** — represents a resource within a space (`get()`, `put()`, `post()`, `delete()`)
- **`StorageResponse`** — wraps HTTP responses (`status`, `ok`, `headers`, `content()`, `json()`, `text()`)

## Scripts

```bash
uv run safety scan
uv run ruff check
uv run flake8 src tests
uv run bandit -r src
uv run bandit -r tests -s B101
uv run -m pytest -vv --cov=src --cov-report=term --cov-report=xml
uv version --bump patch
git add . && git commit -m "Bump patch version" && git tag -sm "New feature" $version
rm -rf dist && uv build
uv publish -t $(keyring get https://upload.pypi.org/legacy/ __token__)
```

## References

- [Wallet Attached Storage Client JavaScript](https://github.com/did-coop/wallet-attached-storage)
- [Wallet Attached Storage Specification (ReSpec Format)](https://github.com/did-coop/wallet-attached-storage-spec)
