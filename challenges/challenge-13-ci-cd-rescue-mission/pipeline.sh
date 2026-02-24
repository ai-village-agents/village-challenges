#!/bin/bash
set -e

echo '>>> STAGE 1: LINTING (flake8)'
flake8 src tests
echo '✅ Linting passed!'

echo '>>> STAGE 2: DEPENDENCY CHECK'
pip install -r requirements.txt --dry-run
echo '✅ Dependencies look valid!'

echo '>>> STAGE 3: UNIT TESTS'
pytest tests
echo '✅ Tests passed!'

echo '>>> STAGE 4: DOCKER BUILD'
docker build -t rescue-mission-app .
echo '✅ Docker build passed!'

echo '🎉 PIPELINE SUCCESS! You saved the day!'
