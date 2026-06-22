# CV Project — Data-driven Architecture

This project generates two CV variants (ModernCV classic + AltaCV) from a single source of truth `cv.json`.

## Structure

```
cvpoly/
├── cv.json                        # Single source of truth (data)
├── cv.schema.json                 # JSON Schema (IDE validation + CI)
├── README.md                      # CI/CD badges + documentation
├── generate_cv.py                 # LaTeX generator (stdlib, dataclasses)
├── altacv.cls                     # AltaCV class bundled in the repo
├── Makefile                       # Automated build workflow
├── release.sh                     # Release script (build + tag + push)
├── picture.png                    # Profile photo
├── .github/
│   ├── dependabot.yml             # Monthly Dependabot checks
│   ├── workflows/compile.yml      # CI/CD build + release (tags v*)
│   └── workflows/validate.yml     # CI validation (every push/PR)
├── build/                         # Generated output
│   ├── cv_moderncv.tex
│   ├── cv_altacv.tex
│   └── *.aux *.log *.out ...
└── out/                           # Ignored (stale)
```

## Workflow

```sh
make docker     # Docker build (reproducible)
make all        # generate + moderncv + altacv
make validate   # Python validation of cv.json
make generate   # cv.json → build/*.tex (includes validate)
make moderncv   # pdflatex → "First Last YYYYMM mod.pdf"
make altacv     # xelatex → "First Last YYYYMM alta.pdf"
make clean      # rm -rf build/ + PDFs (local)
./release.sh    # build + commit + tag + push → triggers CI
```

## CI/CD

- Workflow `validate.yml`: triggered **on every push/PR** to `main` (Python validation of `cv.json`)
- Workflow `compile.yml`: triggered **only** on `git push origin v*`
  - Job `build`: compiles PDFs, uploads as artifact
  - Job `release` (`needs: build`, `permissions: contents: write`): creates a GitHub Release with attached PDFs
- Monthly Dependabot for GitHub Actions and the Docker image

## Principles

- **Data-driven**: edit only `cv.json`, everything else is generated (including filenames from the author)
- **LaTeX escaping** of special characters (%, _, &, $, etc.)
- **Two templates**: ModernCV (classic, pdflatex) and AltaCV (paracol, xelatex)
- **Zero external Python dependencies** (stdlib only)
- **Security**: GitHub Actions pinned by commit SHA, restricted permissions, conditional `driver_license`
- **QR Code + PDF metadata**: link to source code embedded in the PDF
- **Validation**: `cv.schema.json` + `make validate` in CI on every push
