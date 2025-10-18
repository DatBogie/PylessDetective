#!/bin/sh
echo "--- Build Headless Exec ---"

echo Creating venv...
python3 -m venv .venv

echo Activating venv...
source .venv/bin/activate

echo Installing dependancies from requirements.txt...
pip3 install -r requirements.txt

echo Building...
pyinstaller -ycF -n "PylessDetective" --add-data "maps/*.csv:maps/" main.py

echo "--- Build GUI Exec ---"

echo Cleaning up stale venv...
rm -rf ./.venv

echo Creating venv..
python3 -m venv .venv

echo Activating venv...
source .venv/bin/activate

echo Installing dependancies from requirements-gui.txt...
pip3 install -r requirements-gui.txt

echo Building...
pyinstaller -ywF -n "PylessDetectiveGui" --add-data "maps/*.csv:maps/" --add-data "main.py:main.py" gui.py