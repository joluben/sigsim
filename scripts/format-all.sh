#!/bin/bash

# Format all code script

set -e

echo "✨ Formatting all code..."

# Backend formatting
echo "📊 Formatting backend..."
cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run backend formatting
echo "  - Running black..."
black app tests

echo "  - Running isort..."
isort app tests

echo "✅ Backend formatting completed"

# Frontend formatting
echo "📊 Formatting frontend..."
cd ../frontend

echo "  - Running Prettier..."
npm run format

echo "  - Running ESLint fix..."
npm run lint:fix

echo "✅ Frontend formatting completed"

echo "🎉 All code formatted successfully!"