.PHONY: serve

PORT ?= 8000

serve:
	@echo "Running Python main.py to build JS table..."
	python3 user_provided/python/main.py
	@echo "Serving docs on http://localhost:$(PORT)..."
	cd docs && python3 -m http.server $(PORT)
