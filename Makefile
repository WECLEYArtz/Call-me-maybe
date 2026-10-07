all: run

install:
	uv sync

run:
	uv run python3 -m src

lint: 
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


lint-strict:
	uv run flake8 .
	uv run mypy . --strict
