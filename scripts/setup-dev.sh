#!/bin/bash

# Development environment setup script

set -e

echo "🚀 Setting up IoT Simulator development environment..."

# Check if Python 3.11+ is installed
if ! command -v python3.11 &> /dev/null; then
    echo "❌ Python 3.11+ is required but not installed."
    exit 1
fi

# Check if Node.js 18+ is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 18+ is required. Current version: $(node --version)"
    exit 1
fi

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements-dev.txt

echo "✅ Backend setup complete"

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies
npm install

echo "✅ Frontend setup complete"

# Setup pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
cd ..

# Install pre-commit if not already installed
if ! command -v pre-commit &> /dev/null; then
    pip install pre-commit
fi

# Install pre-commit hooks
pre-commit install

echo "✅ Pre-commit hooks installed"

# Create data directory
mkdir -p data

echo "🎉 Development environment setup complete!"
echo ""
echo "To start development:"
echo "  Backend:  cd backend && source venv/bin/activate && make run"
echo "  Frontend: cd frontend && npm run dev"
echo "  Docker:   docker-compose up -d"
echo ""
echo "Useful commands:"
echo "  make help           - Show available commands"
echo "  npm run lint        - Lint frontend code"
echo "  npm run test        - Run frontend tests"
echo "  pytest              - Run backend tests"