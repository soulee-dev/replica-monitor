all: down up test

down:
	@echo "Running docker-compose down..."
	docker-compose down -v

up:
	@echo "Running docker-compose up..."
	docker-compose up -d
	sleep 5

test:
	@echo "Running main.py..."
	python3 main.py

.PHONY: all down up test
