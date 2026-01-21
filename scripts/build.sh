#!/bin/bash
# Build the standalone executable using PyInstaller

echo "Cleaning up old build artifacts..."
rm -rf build dist *.spec

echo "Building standalone executable..."
# --onefile: Create a single executable
# --name: The name of the resulting binary
# --paths src: Helps PyInstaller find your modules
poetry run pyinstaller --onefile --name media-sync --paths src src/main.py

echo "---------------------------------------------"
echo "Build complete! Binary located at: ./dist/media-sync"
echo "---------------------------------------------"
