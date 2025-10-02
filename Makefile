.PHONY: help dev build test lint seed loadtest clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Start all services in development mode
	docker-compose -f docker-compose.dev.yml up --build

build: ## Build all services
	cd gateway && go build -o bin/gateway ./cmd/gateway
	cd api && uv build
	cd worker && uv build
	cd ui && npm run build
	cd ext-chrome && npm run build
	cd sdks/ts && npm run build

test: ## Run all tests
	cd gateway && go test ./...
	cd api && pytest
	cd worker && pytest
	cd ui && npm test
	cd ext-chrome && npm test
	cd sdks/ts && npm test
	cd sdks/python && pytest

lint: ## Lint all code
	cd gateway && golangci-lint run
	cd api && ruff check .
	cd worker && ruff check .
	cd ui && npm run lint
	cd ext-chrome && npm run lint
	cd sdks/ts && npm run lint
	cd sdks/python && ruff check .

seed: ## Seed database with defaults
	cd api && python -m app.seed

loadtest: ## Run k6 load tests
	k6 run ops/scripts/loadtest.js

clean: ## Clean build artifacts
	docker-compose -f docker-compose.dev.yml down -v
	rm -rf gateway/bin api/dist worker/dist ui/.next ui/out ext-chrome/dist