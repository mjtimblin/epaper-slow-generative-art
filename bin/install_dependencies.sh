#!/bin/bash

set -e

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"

sudo apt-get install -y cmake python3 python3-pip

if [ ! -d "$REPO_ROOT/XNNPACK" ]; then
  cd "$REPO_ROOT"
  git clone https://github.com/google/XNNPACK.git
  cd XNNPACK
  hash="$(git rev-list -n 1 --before="2023-06-27 00:00" master)"
  git checkout $hash
  mkdir build
  cd build
  cmake -DXNNPACK_BUILD_TESTS=OFF -DXNNPACK_BUILD_BENCHMARKS=OFF ..
  cmake --build . --config Release
fi

if [ ! -d "$REPO_ROOT/OnnxStream" ]; then
  cd "$REPO_ROOT"
  git clone https://github.com/vitoplantamura/OnnxStream.git
  cd OnnxStream/src
  mkdir build
  cd build
  cmake -DMAX_SPEED=ON -DXNNPACK_DIR="$REPO_ROOT/XNNPACK" ..
  cmake --build . --config Release
fi

if [ ! -d "$REPO_ROOT/weights" ]; then
  cd "$REPO_ROOT"
  mkdir weights
  cd weights
  wget -O weights.zip "https://github.com/mjtimblin/epaper-slow-generative-art/releases/download/v0.1/weights.zip"
  unzip weights.zip
  rm -rf weights.zip
fi

# Install pip dependencies to virtualenv
if [ ! -d "$REPO_ROOT/venv" ]; then
  cd "$REPO_ROOT"
  python -m pip install virtualenv
  python -m virtualenv venv
  source venv/bin/activate
  python -m pip install -r requirements.txt
fi
