PYTHON       = python3
BUILD_DIR    = build
MODERNCV_TEX = $(BUILD_DIR)/cv_moderncv.tex
ALTACV_TEX   = $(BUILD_DIR)/cv_altacv.tex
AUTHOR       = $(shell $(PYTHON) -c "import json; d=json.load(open('cv.json'))['personal_info']['name']; print(d['first']+' '+d['family'])")
DATE         = $(shell date +%Y%m)
MODERNCV_PDF = $(AUTHOR) $(DATE) mod.pdf
ALTACV_PDF   = $(AUTHOR) $(DATE) alta.pdf

.PHONY: all init validate generate moderncv altacv compile clean docker

# Default: full local build (requires pdflatex + xelatex on host)
all: generate moderncv altacv

# Docker build (portable, no local LaTeX needed)
docker:
	docker compose run --rm cv

init:
	mkdir -p $(BUILD_DIR)
	$(PYTHON) -c "import json, dataclasses; print('[OK] Python dependencies check passed')"

validate:
	$(PYTHON) generate_cv.py validate

generate: init validate
	$(PYTHON) generate_cv.py

moderncv: generate
	-cd $(BUILD_DIR) && pdflatex -interaction=nonstopmode cv_moderncv.tex
	-cd $(BUILD_DIR) && pdflatex -interaction=nonstopmode cv_moderncv.tex
	-mv "$(BUILD_DIR)/cv_moderncv.pdf" "$(MODERNCV_PDF)"
	@echo "[OK] $(MODERNCV_PDF)"

altacv: generate
	cp altacv.cls $(BUILD_DIR)/
	-cd $(BUILD_DIR) && xelatex -interaction=nonstopmode cv_altacv.tex
	-cd $(BUILD_DIR) && xelatex -interaction=nonstopmode cv_altacv.tex
	-rm $(BUILD_DIR)/altacv.cls
	-mv "$(BUILD_DIR)/cv_altacv.pdf" "$(ALTACV_PDF)"
	@echo "[OK] $(ALTACV_PDF)"

compile: moderncv altacv

clean:
	rm -rf $(BUILD_DIR) "$(MODERNCV_PDF)" "$(ALTACV_PDF)"
	@echo "[OK] Cleaned"
