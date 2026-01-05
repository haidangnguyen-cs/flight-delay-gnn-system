# Makefile - Flight Delay GNN System
# Author: Hai Dang Nguyen
# Description: Central control for all pipelines (Local & Docker)

.PHONY: help install ingest archive train dashboard inference-py inference-spark clean

ifeq ($(OS),Windows_NT)
    SHELL := powershell.exe
    .SHELLFLAGS := -NoProfile -Command
    PYTHON_CMD := $$env:PYTHONPATH='.'; uv run python
    STREAMLIT_CMD := $$env:PYTHONPATH='.'; uv run streamlit run
else
    PYTHON_CMD := PYTHONPATH=. uv run python
    STREAMLIT_CMD := PYTHONPATH=. uv run streamlit run
endif

# --- 1. SETUP & HELP ---
help:
	@echo "======================================================================"
	@echo "     FLIGHT DELAY GNN SYSTEM - CONTROL PANEL"
	@echo "======================================================================"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install          Install dependencies
	@echo "  dashboard        Run Streamlit Dashboard (Local)"
	@echo "  ingest           Run Data Ingestion Pipeline (Local -> Kafka)"
	@echo "  archive          Run Data Archiving Pipeline (Kafka -> Cassandra)"
	@echo "  train            Run Model Training Pipeline (Local GPU/CPU)"
	@echo "  inference-py     Run Python Inference Pipeline (Local)"
	@echo "  inference-spark  Run Spark Inference Pipeline (Inside Docker Container)"
	@echo "======================================================================"

install: ## Setup environment using uv
	@echo "Installing dependencies..."
	@uv sync

# --- 2. DATA PIPELINES (LOCAL) ---
ingest:
	@echo "Starting Ingestion Pipeline..."
	@$(PYTHON_CMD) -m src.pipelines.ingestion

archive:
	@echo "Starting Archiving Pipeline..."
	@$(PYTHON_CMD) -m src.pipelines.data_archiving

# --- 3. TRAINING (LOCAL) ---
train:
	@echo "Starting Training Pipeline..."
	@$(PYTHON_CMD) -m src.pipelines.training_pipeline

# --- 4. INFERENCE (HYBRID) ---
inference-py:
	@echo "Starting Python Inference..."
	@$(PYTHON_CMD) -m src.pipelines.python_inference_pipeline

inference-spark:
	@echo "Executing Spark Pipeline inside 'inference-driver' container..."
	@docker exec -u 0 -it inference-driver python -m src.pipelines.spark_inference_pipeline

# --- 5. DASHBOARD (LOCAL) ---
dashboard:
	@echo "Launching Dashboard..."
	@$(STREAMLIT_CMD) src/dashboard/main.py
