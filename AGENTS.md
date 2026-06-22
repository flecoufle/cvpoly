# CV Project — Architecture Data-driven

Ce projet génère deux variantes de CV (ModernCV classic + AltaCV) à partir d'une source de vérité unique `cv.json`.

## Structure

```
cvpoly/
├── cv.json                        # Source de vérité unique (données)
├── cv.schema.json                 # JSON Schema (validation IDE + CI)
├── README.md                      # Badges CI/CD + documentation
├── generate_cv.py                 # Générateur LaTeX (stdlib, dataclasses)
├── altacv.cls                     # Classe AltaCV packagée dans le dépôt
├── Makefile                       # Workflow automatisé
├── release.sh                     # Script de release (build + tag + push)
├── picture.png                    # Photo
├── .github/
│   ├── dependabot.yml             # Dependabot mensuel
│   ├── workflows/compile.yml      # CI/CD build + release (tags v*)
│   └── workflows/validate.yml     # CI validation (every push/PR)
├── build/                         # Généré
│   ├── cv_moderncv.tex
│   ├── cv_altacv.tex
│   └── *.aux *.log *.out ...
└── out/                           # Ignoré (stale)
```

## Workflow

```sh
make docker     # docker build
make all        # generate + moderncv + altacv
make validate   # validation Python de cv.json
make generate   # cv.json → build/*.tex (inclut validate)
make moderncv   # pdflatex → "Prénom Nom YYYYMM mod.pdf"
make altacv     # xelatex → "Prénom Nom YYYYMM alta.pdf"
make clean      # rm -rf build/ + PDFs (local)
./release.sh    # build + commit + tag + push → déclenche CI
```

## CI/CD

- Workflow `validate.yml` : déclenché **sur chaque push/PR** sur `main` (validation Python de `cv.json`)
- Workflow `compile.yml` : déclenché **uniquement** sur `git push origin v*`
  - Job `build` : compile les PDF, upload en artifact
  - Job `release` (`needs: build`, `permissions: contents: write`) : crée une GitHub Release avec les PDF attachés
- Dependabot mensuel pour les actions GitHub et l'image Docker

## Principes

- **Data-driven** : éditer `cv.json` uniquement, le reste est généré (y compris les noms de fichiers depuis l'auteur)
- **Échappement LaTeX** automatique des caractères spéciaux (%, _, &, $, etc.)
- **Échappement LaTeX** automatique des caractères spéciaux (%, _, &, $, etc.)
- **Deux templates** : ModernCV (classic, pdflatex) et AltaCV (paracol, xelatex)
- **Zéro dépendance Python** externe (stdlib seulement)
- **Sécurité** : actions GitHub épinglées par SHA, permissions restreintes, `driver_license` conditionnel
- **QR Code + métadonnées PDF** : lien vers le code source intégré dans le PDF
- **Validation** : `cv.schema.json` + `make validate` en CI sur chaque push
