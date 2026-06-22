# CV Polyglot

[![Build](https://github.com/flecoufle/cvpoly/actions/workflows/compile.yml/badge.svg)](https://github.com/flecoufle/cvpoly/actions/workflows/compile.yml)
[![Validate](https://github.com/flecoufle/cvpoly/actions/workflows/validate.yml/badge.svg)](https://github.com/flecoufle/cvpoly/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/flecoufle/cvpoly)](https://github.com/flecoufle/cvpoly/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Data-driven** CV generator — edit `cv.json`, get two professionally typeset PDFs (ModernCV + AltaCV), versioned and delivered via GitHub Releases.

## How it works

A single source of truth (`cv.json`) is processed by a pure-Python generator (stdlib only, zero external dependencies) into LaTeX source, then compiled to PDF via Docker.

## Workflow

```sh
make docker          # Docker build (reproducible, no local LaTeX needed)
make all             # generate + moderncv + altacv
make validate        # validate cv.json
make generate        # cv.json → build/*.tex
./release.sh         # build + tag + push → triggers GitHub Release
```

## Project structure

```
cv.json              # Single source of truth (all CV data)
cv.schema.json       # JSON Schema (IDE validation + CI)
generate_cv.py       # LaTeX generator (stdlib, dataclasses)
altacv.cls           # AltaCV class bundled in the repo
Makefile             # Automated build workflow
release.sh           # Release script (build + tag + push)
LICENSE              # MIT License
at.pdf               # @ symbol image (anti-scraping)
picture.png          # Profile photo
```

## Outputs

Two CV variants are compiled:

| Variant | Engine | Style |
|---------|--------|-------|
| **ModernCV** | pdflatex | Classic, blue, sans-serif |
| **AltaCV** | xelatex | Modern, two-column, serif headings |

PDF filenames are auto-generated from the author name and build date (e.g. `John Doe 202606 mod.pdf`).

## Security

- CI/CD actions pinned by commit SHA
- Restricted workflow permissions
- No external Python dependencies
- Email obfuscation via embedded `@` image to hinder scraping
- `driver_license` field rendered conditionally

## Validation

JSON Schema validation runs on every push/PR via `.github/workflows/validate.yml`.

## Built with

- Python 3 (stdlib only — `json`, `dataclasses`, `re`)
- LaTeX (ModernCV + AltaCV)
- Docker (reproducible build environment)
- GitHub Actions (CI/CD + Release automation)

## License

MIT — see [LICENSE](LICENSE).
