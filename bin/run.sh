#!/bin/bash

set -e

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"
cd "$REPO_ROOT"

source venv/bin/activate

export PYTHONPATH="$PYTHONPATH:$REPO_ROOT/src"

venv/bin/python src/generate_image.py

# Remove the next line to store the generated images
find "$REPO_ROOT/generated" -type f -name '*.png' -not -name 'latest_sd_with_caption.png' -not -name 'latest_qrcode_with_caption.png' -delete
