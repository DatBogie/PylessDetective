@echo off
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
pyinstaller --clean -ycF -n "PylessDetective" --add-data "maps/*.csv;maps/" main.py

rmdir /s /q .\.venv

python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements-gui.txt
pyinstaller --clean -ywF -n "PylessDetectiveGui" --add-data "maps/*.csv;maps/" --add-data "main.py;main.py" gui.py