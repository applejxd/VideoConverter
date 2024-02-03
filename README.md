# VideoConverter

Python CLI (Fire) and GUI (Tkinter) interface examples for ffmpeg-python

## Install dependencies

For Windows 11:

```powershell
# Install command
winget install ffmpeg

# Install dependencies
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# Library install
pip install -e .
# GUI executable creation
pyinstaller .\video_converter\gui.py --onefile --noconsole
```

## How to use

```powershell
# Open GUI
python -m video_conveter open_window
```
