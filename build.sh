#!/bin/bash
pyinstaller -ycF -n "PylessDetective" --add-data "maps/*.csv:maps/" main.py