test:
	uv run python -m unittest discover tests

format-check:
	uv run black --check .

.PHONY: format-check test
