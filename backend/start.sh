#!/bin/bash
# Startup script for Render deployment
uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}

