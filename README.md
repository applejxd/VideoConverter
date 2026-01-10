# VideoConverter

Python CLI (Fire) and GUI (Tkinter) interface examples for ffmpeg-python

## Install dependencies

For Windows 11:

```powershell
# Install command
winget install astral-sh.uv Gyan.FFmpeg

# Install dependencies
uv sync

# GUI executable creation
pyinstaller .\video_converter\gui.py --onefile --noconsole
```

## How to use

```powershell
# Open GUI
python -m video_converter gui

# Compress video
python -m video_converter compress input.mp4 --crf 23

# Convert video to mp4
python -m video_converter to_mp4 input.mov

# Eliminate audio from video
python -m video_converter audio_eliminate input.mp4

# Extract audio from video
python -m video_converter audio_extract input.mp4
```

## How to develop

```bash
uv sync --dev
pre-commit install

# optional
pre-commit run --all-files
```
