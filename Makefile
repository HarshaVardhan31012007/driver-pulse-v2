# Driver Pulse Makefile
# Common development and deployment tasks

.PHONY: help install run clean docker-build docker-run generate-data lint format check

help:
	@echo "Driver Pulse - Available Commands:"
	@echo "  install      Install dependencies"
	@echo "  run          Run dashboard"
	@echo "  pipeline     Run full data processing pipeline"
	@echo "  clean        Clean generated files"
	@echo "  generate-data Generate sample data"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run with Docker"
	@echo "  lint         Lint code"
	@echo "  format       Format code"
	@echo "  check        Check for errors"

install:
	pip install -r requirements.txt

run:
	@echo "Starting dashboard..."
	streamlit run dashboard/app.py

pipeline:
	@echo "Running data processing pipeline..."
	python main.py --generate-sample-data

clean:
	@echo "Cleaning generated files..."
	rm -rf outputs/* data/* __pycache__ */__pycache__

generate-data:
	@echo "Generating sample data..."
	python main.py --generate-sample-data

docker-build:
	@echo "Building Docker image..."
	docker build -t driver-pulse .

docker-run:
	@echo "Running with Docker..."
	docker-compose up --build

lint:
	@echo "Linting code..."
	flake8 . --max-line-length=100

format:
	@echo "Formatting code..."
	black .

check:
	@echo "Checking for errors..."
	python -m py_compile main.py
	python -m py_compile signal_processing/*.py
	python -m py_compile dashboard/*.py
