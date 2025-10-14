@echo off
pyinstaller --clean -ycF -n "PylessDetective" --add-data "maps/*.csv;maps/" main.py