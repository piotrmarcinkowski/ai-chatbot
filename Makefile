# Makefile for AI Chatbot Production Deployment
# 
# This automates the two-step process required for proper production deployment:
# 1. Build production image with 'langgraph build'
# 2. Run with docker compose

.PHONY: help build-prod up-prod down clean rebuild

# Default target
help:
	@echo "AI Chatbot - Production Deployment"
	@echo "==================================="
	@echo ""
	@echo "Available targets:"
	@echo "  make build-prod  - Build production image using 'langgraph build'"
	@echo "  make up-prod     - Start production environment (builds if needed)"
	@echo "  make down        - Stop all containers"
	@echo "  make rebuild     - Rebuild and restart everything"
	@echo "  make clean       - Stop containers and remove images"
	@echo ""

# Build production image using langgraph build
build-prod:
	@echo "Building production image..."
	@cd app/src && langgraph build -t ai-chatbot-prod:latest
	@echo "✅ Production image built successfully!"

# Start production environment
up-prod: build-prod
	@echo "Starting production environment..."
	@docker compose -f docker-compose.prod.yml up -d
	@echo "✅ Production environment started!"
	@echo ""
	@echo "Server available at: http://localhost:8123"
	@echo "Health check: curl http://localhost:8123/ok"

# Stop containers
down:
	@docker compose -f docker-compose.prod.yml down

# Rebuild everything
rebuild: down build-prod up-prod

# Clean up everything
clean: down
	@docker rmi ai-chatbot-prod:latest || true
	@echo "✅ Cleaned up!"
