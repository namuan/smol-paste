export PROJECTNAME=$(shell basename "$(PWD)")

.DEFAULT_GOAL := default

.PHONY: default install lint test upgrade build clean

default: install lint test

install:
	uv sync --all-extras --dev

lint:
	uv run python devtools/lint.py

test:
	uv run pytest

upgrade:
	uv sync --upgrade

build:
	uv build

run: ## Run the application
	@echo "🚀 Testing code: Running"
	uv run $(PROJECTNAME)

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +