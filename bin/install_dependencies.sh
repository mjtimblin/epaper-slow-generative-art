#!/bin/bash

set -e

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." >/dev/null 2>&1 && pwd )"

sudo apt-get install -y cmake unrar

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
  cd OnnxStream
  cd src
  mkdir build
  cd build
  cmake -DMAX_SPEED=ON -DXNNPACK_DIR="$REPO_ROOT/XNNPACK" ..
  cmake --build . --config Release
fi

# Download weights if they are not already present (.gitignore won't be represented in the count since it's a hidden file)
num_files_in_weights_dir=$(ls -1q "$REPO_ROOT/weights" | wc -l)
if [ $num_files_in_weights_dir -eq 0 ]; then
  cd "$REPO_ROOT/weights"
  wget -O weights.rar "https://github.com/vitoplantamura/OnnxStream/releases/download/v0.1/StableDiffusion-OnnxStream-Windows-x64-with-weights.rar"
  unrar x weights.rar
  mv SD/* .
  rm -rf SD weights.rar sd.exe
fi
