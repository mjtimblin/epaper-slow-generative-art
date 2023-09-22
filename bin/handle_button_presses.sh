#!/bin/bash

set -e

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$REPO_ROOT"

source venv/bin/activate

export PYTHONPATH="$PYTHONPATH:$REPO_ROOT/src"

venv/bin/python src/handle_buttons.py
