#!/usr/bin/env bash
# Inicia o backend com reload rápido — monitora só o código-fonte,
# ignora .venv (217MB), data/, dataset/ e __pycache__
uvicorn main:app \
  --reload \
  --reload-dir . \
  --reload-exclude ".venv" \
  --reload-exclude "data" \
  --reload-exclude "dataset" \
  --reload-exclude "__pycache__" \
  --reload-exclude "*.pyc" \
  --host 0.0.0.0 \
  --port 8000
