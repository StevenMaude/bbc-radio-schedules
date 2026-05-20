test:
uv run python -m pytest tests/

test-unit:
uv run python -m pytest tests/test_api.py

test-functional:
uv run python -m pytest tests/test_functional.py

lint:
uv run ruff check .
uv run ruff format --check .

.PHONY: test test-unit test-functional lint
