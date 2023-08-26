all: down up test

down:
	@echo "Running docker-compose down..."
	docker-compose down -v

up:
	@echo "Running docker-compose up..."
	docker-compose up -d

test:
	@echo "Running test.py..."
	python3 test.py

.PHONY: all down up test
