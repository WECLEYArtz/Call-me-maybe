all: run

install:
	uv sync

run:
	uv run python3 -m src
