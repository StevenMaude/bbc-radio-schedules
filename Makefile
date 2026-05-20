format:
	uv run --python 3.13 black bbcradio tests

test:
	uv run python -m unittest discover tests/

.PHONY: format test
