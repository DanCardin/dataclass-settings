.PHONY: install test lint format

install:
	uv sync

test:
	uv run coverage run -m pytest src tests
	uv run coverage combine
	uv run coverage report
	uv run coverage xml

lint:
	uv run ruff check src tests || exit 1
	uv run mypy src tests || exit 1
	uv run ruff format --check --diff src tests || exit 1

format:
	uv run ruff check --fix src tests
	uv run ruff format src tests
