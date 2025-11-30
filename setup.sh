#!/bin/bash

# Auto-Ops-AI Startup Script

echo "========================================="
echo "Auto-Ops-AI Backend Setup"
echo "========================================="

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "Creating .env file from template..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your API keys!"
    echo ""
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data/processed data/raw logs

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your API keys (GOOGLE_API_KEY or OPENAI_API_KEY)"
echo "2. Place your ticketing data in data/raw/ticketing_system_data_new.json"
echo "3. Run the server:"
echo "   cd backend && uvicorn app.main:app --reload"
echo ""
echo "Or use Docker:"
echo "   docker-compose up --build"
echo ""
