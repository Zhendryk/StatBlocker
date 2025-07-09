@echo off

REM Create virtual environment in statblocker/_venv
python -m venv _venv

REM Upgrade pip in the venv
_venv\Scripts\python.exe -m pip install --upgrade pip

REM Install the project from the parent directory (where pyproject.toml is)
_venv\Scripts\python.exe -m pip install ..
_venv\Scripts\python.exe -m pip install "..[dev]"

REM Optionally activate the virtual environment (for interactive use)
call _venv\Scripts\activate.bat

echo Virtual Environment setup complete!