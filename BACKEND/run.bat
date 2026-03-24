@echo off
echo Starting Code Nest Backend...

:: Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate venv
call venv\Scripts\activate

:: Install requirements if needed
echo Installing dependencies...
pip install -r requirements.txt

:: Run the application
echo Starting Flask server...
python run.py
pause
