#!/bin/bash
echo "Installing AVARIS dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Dependencies installed successfully!"
