# VideoConverter

Python CLI (Fire) and GUI (Tkinter) interface examples for ffmpeg-python

## Install dependencies

For Windows 11:

```powershell
winget install ffmpeg

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

pip install -r requirements.txt

pyinstaller gui.py --onefile
```
