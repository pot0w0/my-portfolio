#!/usr/bin/env sh

cd tools

uvicorn --reload --port 3000 fake_backend:app