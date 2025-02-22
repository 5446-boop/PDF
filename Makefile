.PHONY: install install-dev test lint format clean build

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest tests/ --cov=pdf_highlighter

lint:
	flake8 src tests
	mypy src
	black --check src tests
	isort --check-only src tests

format:
	black src tests
	isort src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

build:
	python -m build