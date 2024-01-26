# VideoConverter

Python CLI (Fire) and GUI (Tkinter) interface examples for ffmpeg-python

## Install dependencies

For Windows 11:

```powershell
winget install ffmpeg

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

pip install -e .

pyinstaller .\video_converter\gui.py --onefile
```

## How to use

```powershell
# Open GUI
python -m video_conveter open_window
```
