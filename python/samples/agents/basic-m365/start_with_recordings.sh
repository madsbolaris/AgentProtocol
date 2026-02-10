#!/bin/bash
export USE_LLM_RECORDINGS=true
cd "$(dirname "$0")"
python3 src/main.py
