.PHONY: install
install: ## Install the environment and the pre-commit hooks
	@echo "🚀 Creating virtual environment"
	@uv sync
	@uv run pre-commit install

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking uv lock file consistency with 'pyproject.toml': Running uv lock --check"
	@uv sync --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a

.PHONY: format
format: ## Format code based on code quality tools.
	@echo "🚀 Checking uv lock file consistency with 'pyproject.toml': Running uv lock --check"
	@uv sync --check
	@echo "🚀 Linting code: Running ruff format"
	@uv run ruff format .
	@echo "🚀 Linting code: Running ruff check"
	@uv run ruff check --fix .

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run pytest tests

.PHONY: tox
tox: ## Test the code with pytest
	@echo "🚀 Testing code: Running tox"
	@uv run tox 

.PHONY: build
build: clean-build ## Build wheel file using uv
	@echo "🚀 Creating wheel file"
	@uv build

.PHONY: clean-build
clean-build: ## clean build artifacts
	@rm -rf dist

.PHONY: publish
publish: ## publish a release to pypi.
	@echo "🚀 Publishing: Dry run."
	@UV_PYPI_TOKEN="$(PYPI_TOKEN)" uv publish --dry-run
	@echo "🚀 Publishing."
	@UV_PYPI_TOKEN="$(PYPI_TOKEN)" uv publish

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
