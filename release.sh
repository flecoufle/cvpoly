#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v$(date +%Y%m%d)}"

echo "[*] Tagging release: $VERSION"
make docker

# Update RELEASE.md with $VERSION at the top so the changelog is up to date in the GitHub release
echo "# Release $VERSION" > RELEASE.md

git add -A
git commit -m "release: $VERSION" || true

#gh release delete "$VERSION" -y 2>/dev/null || true
git tag -f "$VERSION"
git push -f origin HEAD refs/tags/"$VERSION"

echo "[OK] Release $VERSION pushed — workflow triggered"
