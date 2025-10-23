@echo off
echo ===================================
echo Perplexity AI Wrapper - Installer
echo ===================================

python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium

if not exist logs mkdir logs
if not exist exports mkdir exports
if not exist screenshots mkdir screenshots
if not exist .cache mkdir .cache

if not exist .env copy .env.example .env

echo.
echo Installation complete!
echo   Activate: venv\Scripts\activate
echo   Test: python quick_test.py
pause
