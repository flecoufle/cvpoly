#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-v$(date +%Y%m%d)}"

echo "[*] Tagging release: $VERSION"
make docker

# Met à jour RELEASE.md avec $VERSION en début de fichier pour que le changelog soit à jour dans la release GitHub
echo "# Release $VERSION" > RELEASE.md

git add -A
git commit -m "release: $VERSION" || true

git tag "$VERSION"
git push origin "$VERSION"

echo "[OK] Release $VERSION pushed — workflow déclenché"
