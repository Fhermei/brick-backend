#!/bin/bash
echo "Starting on port: ${PORT:-10000}"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files in src: $(ls -la src/)"
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-10000} --log-level debug