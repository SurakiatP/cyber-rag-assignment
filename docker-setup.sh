#!/bin/bash

# Docker Setup Script for Cyber-RAG
# This script pulls necessary Ollama models before starting the application

set -e

echo "========================================="
echo "Cyber-RAG Docker Setup"
echo "========================================="

# Quick check for pre-ingested data (inline)
echo "Step 1: Checking pre-ingested data..."
INGESTED_FILE="ingested_data/ingested_documents.json"

if [ -f "$INGESTED_FILE" ]; then
    FILE_SIZE=$(stat -f%z "$INGESTED_FILE" 2>/dev/null || stat -c%s "$INGESTED_FILE" 2>/dev/null)
    FILE_SIZE_MB=$(echo "scale=2; $FILE_SIZE / 1024 / 1024" | bc 2>/dev/null || echo "0")
    echo "✓ Found: $INGESTED_FILE ($FILE_SIZE_MB MB)"
    echo "  Startup will be fast (2-5 minutes)"
else
    echo "⚠ Warning: $INGESTED_FILE not found"
    echo "  First startup will take 10-30 minutes for data ingestion"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check for NVIDIA GPU support
if ! docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi > /dev/null 2>&1; then
    echo "Warning: NVIDIA GPU not detected or docker GPU support not configured"
    echo "The system will run on CPU which will be significantly slower"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start Ollama service first
echo "Starting Ollama service..."
docker-compose up -d ollama

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until docker exec cyber-rag-ollama ollama list > /dev/null 2>&1; do
    echo "Waiting for Ollama service..."
    sleep 5
done

echo "Ollama is ready!"

# Pull required models
echo "Pulling Ollama models (this may take a while)..."

echo "1/2 Pulling Typhoon 2.1 (Query Expansion)..."
docker exec cyber-rag-ollama ollama pull scb10x/typhoon2.1-gemma3-4b:latest

echo "2/2 Pulling Qwen 2.5 7B (Answer Generation)..."
docker exec cyber-rag-ollama ollama pull qwen2.5:7b-instruct-q4_0

echo "All models pulled successfully!"

# Give Ollama extra time to fully initialize after pulling models
echo "Waiting for Ollama to fully initialize..."
sleep 10

# Start the main application
echo "Starting Cyber-RAG application..."
docker-compose up -d cyber-rag

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Application will be available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f cyber-rag"
echo "  - Stop: docker-compose down"
echo "  - Restart: docker-compose restart cyber-rag"
echo ""