# Wallet Attached Storage Client

Python client library for the [Wallet Attached Storage](https://wallet.storage/spec) specification.

## Installation

```bash
pip install wallet-attached-storage-client
```

## Usage

```python
import json
from wallet_attached_storage_client import Ed25519Signer, StorageClient

# Generate a new Ed25519 key pair (or pass your own Ed25519PrivateKey)
signer = Ed25519Signer()
print(f"Signer DID: {signer.id}")  # did:key:z6Mk...

with StorageClient("https://your-was-server.example") as client:

    # 1. Create a space (auto-generates a urn:uuid)
    space = client.space(signer=signer)
    print(f"Space: {space.id}")
    print(f"Path:  {space.path}")

    # 2. Write a resource into the space
    resource = space.resource("/hello.txt")
    put_resp = resource.put(b"Hello from Python!", "text/plain")
    print(f"PUT  {resource.path} -> {put_resp.status}")  # 204

    # 3. Read it back
    get_resp = resource.get()
    print(f"GET  {resource.path} -> {get_resp.status}")  # 200
    print(f"Body: {get_resp.text()}")                     # Hello from Python!

    # 4. Overwrite with JSON
    doc = json.dumps({"greeting": "hi", "from": "python"}).encode()
    resource.put(doc, "application/json")
    print(f"JSON: {resource.get().json()}")

    # 5. Delete the resource
    del_resp = resource.delete()
    print(f"DEL  {resource.path} -> {del_resp.status}")  # 204

    # 6. Confirm it's gone
    gone_resp = resource.get()
    print(f"GET  {resource.path} -> {gone_resp.status}")  # 404
```

### Custom Signers

`Ed25519Signer` is built in, but any object that satisfies the `Signer` protocol
works — you are not locked into a specific cryptography library:

```python
class MySigner:
    @property
    def id(self) -> str:
        """Return a DID key identifier, e.g. did:key:z6Mkh..."""
        ...

    def sign(self, data: bytes) -> bytes:
        """Sign raw bytes and return the raw signature bytes."""
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
