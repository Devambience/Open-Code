#!/bin/bash
echo "Building Open Code IDE..."
pyinstaller --windowed --onefile --add-data "assets:assets" --name "OpenCodeIDE" main.py
echo "Build complete! Check the 'dist' folder."
