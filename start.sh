#!/bin/bash
echo "Starting application on port ${PORT:-10000}"
echo "Current directory: $(pwd)"
echo "Python path: $(which python)"
echo "Starting uvicorn..."
exec uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-10000} --log-level debug