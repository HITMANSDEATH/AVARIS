@echo off
echo Installing AVARIS dependencies...
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
echo Dependencies installed successfully!
pause
