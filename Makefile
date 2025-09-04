.PHONY: help install test lint format clean run docker-build docker-run docker-stop

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e .

test: ## Run tests
	pytest src/tests/ -v --cov=src

test-watch: ## Run tests in watch mode
	pytest src/tests/ -v --cov=src --watch

lint: ## Run linting
	flake8 src/
	mypy src/
	black --check src/

format: ## Format code
	black src/
	isort src/

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/

run: ## Run the Streamlit application
	streamlit run src/ui/main.py

docker-build: ## Build Docker image
	docker build -t pdf-extractor .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup: ## Initial setup
	mkdir -p data uploads logs
	cp env.example .env
	@echo "Please edit .env file with your OpenAI API key"

db-init: ## Initialize database
	python -c "from src.models.database import DatabaseManager; DatabaseManager()"

check: ## Check system requirements
	@echo "Checking Python version..."
	@python --version
	@echo "Checking pip..."
	@pip --version
	@echo "Checking if OpenAI API key is set..."
	@if [ -z "$$OPENAI_API_KEY" ]; then echo "Warning: OPENAI_API_KEY not set"; else echo "OpenAI API key is set"; fi

deploy: ## Deploy to production (placeholder)
	@echo "Deployment not implemented yet"
	@echo "Consider using Docker or cloud deployment services"
