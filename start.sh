#!/bin/bash
# Startup script for OCR microservice

echo "Starting OCR Microservice..."

# Activate virtual environment if it exists
if [ -d "myenv" ]; then
    echo "Activating virtual environment..."
    source myenv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Warning: No virtual environment found. Using system Python."
fi

# Install requirements if not already installed
echo "Installing requirements..."
pip install -r requirements.txt

# Start the application
echo "Starting the FastAPI application..."
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

echo "OCR Microservice stopped."