#!/bin/bash
echo "==================================="
echo "Perplexity AI Wrapper - Installer"
echo "==================================="

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium

mkdir -p logs exports screenshots .cache debug/raw_responses

if [ ! -f .env ]; then
    cp .env.example .env
fi

echo ""
echo "✓ Installation complete!"
echo "  Activate: source venv/bin/activate"
echo "  Test: python quick_test.py"
