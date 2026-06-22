# CV Polyglotte

[![Build](https://github.com/flecoufle/cvpoly/actions/workflows/compile.yml/badge.svg)](https://github.com/flecoufle/cvpoly/actions/workflows/compile.yml)
[![Validate](https://github.com/flecoufle/cvpoly/actions/workflows/validate.yml/badge.svg)](https://github.com/flecoufle/cvpoly/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/flecoufle/cvpoly)](https://github.com/flecoufle/cvpoly/releases)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker)](https://github.com/flecoufle/cvpoly/pkgs/container/cvpoly)

CV **data-driven** généré depuis `cv.json` — source de vérité unique.

## Principe

Une seule édition dans `cv.json` → deux PDF automatiquement compilés
(ModernCV + AltaCV), versionnés et livrés via GitHub Releases.

## Workflow

```sh
make docker          # build dans Docker (reproductible)
make all             # generate + moderncv + altacv
make validate        # valide cv.json
make generate        # cv.json → build/*.tex
./release.sh         # build + tag + push → GitHub Release
```

L'infrastructure complète est visible dans le code source de ce dépôt :
[JSON Schema](cv.schema.json), CI/CD, générateur Python (stdlib pure),
classes LaTeX packagées, obfuscation anti-scraping.

Les PDFs finaux sont téléchargeables depuis les
[Releases](https://github.com/flecoufle/cvpoly/releases).
