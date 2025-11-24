.PHONY: install
install: ## Install the uv environment
	@echo "🚀 Creating virtual environment using uv"
	uv sync	


.PHONY: format
format: ## Format code based on code quality tools.
	@echo "🚀 Linting code: Running ruff format"
	ruff format .
	@echo "🚀 Linting code: Running ruff check"
	ruff check --fix .

.PHONY: test
test: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	pytest tests

.PHONY: tox
tox: ## Test the code with pytest
	@echo "🚀 Testing code: Running tox"
	tox
