#!/bin/bash

# Lint all code script

set -e

echo "🔍 Linting all code..."

# Backend linting
echo "📊 Linting backend..."
cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run backend linting
echo "  - Running flake8..."
flake8 app tests

echo "  - Running mypy..."
mypy app

echo "  - Checking black formatting..."
black --check app tests

echo "  - Checking isort..."
isort --check-only app tests

echo "✅ Backend linting completed"

# Frontend linting
echo "📊 Linting frontend..."
cd ../frontend

echo "  - Running ESLint..."
npm run lint

echo "  - Checking Prettier formatting..."
npm run format:check

echo "✅ Frontend linting completed"

echo "🎉 All linting completed successfully!"