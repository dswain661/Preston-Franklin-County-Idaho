@echo off
echo Starting Local Laws Dashboard...
echo Open http://localhost:8765 in your browser
cd /d "%~dp0"
python -m http.server 8765