#!/bin/bash

# Run all tests script

set -e

echo "🧪 Running all tests..."

# Backend tests
echo "📊 Running backend tests..."
cd backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run backend tests
pytest --cov=app --cov-report=term-missing --cov-report=html

echo "✅ Backend tests completed"

# Frontend tests
echo "📊 Running frontend tests..."
cd ../frontend

# Run frontend tests
npm run test:coverage

echo "✅ Frontend tests completed"

echo "🎉 All tests completed successfully!"
echo ""
echo "Coverage reports:"
echo "  Backend:  backend/htmlcov/index.html"
echo "  Frontend: frontend/coverage/lcov-report/index.html"