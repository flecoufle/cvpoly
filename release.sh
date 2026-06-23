#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v$(date +%Y%m%d)}"

echo "[*] Tagging release: $VERSION"
make docker

# Update RELEASE.md with $VERSION at the top so the changelog is up to date in the GitHub release
echo "# Release $VERSION" > RELEASE.md

git add -A
git commit -m "release: $VERSION" || true

git tag "$VERSION"
git push origin HEAD --tags

echo "[OK] Release $VERSION pushed — workflow triggered"
