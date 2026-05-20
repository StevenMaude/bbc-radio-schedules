test:
python3 -m pytest tests/test_api.py -v

functional-test:
python3 -m pytest tests/test_functional.py -v

.PHONY: test functional-test
