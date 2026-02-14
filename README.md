# Wallet Attached Storage Client

This package is a Python client library for the [Wallet Attached Storage](https://wallet.storage/spec).

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
