# VideoConverter

Python CLI (Fire) and GUI (Tkinter) interface examples for ffmpeg-python.

📖 **[Documentation](https://applejxd.github.io/VideoConverter/)**

## Features

| Command | Description | Default output |
| --- | --- | --- |
| `compress` | Re-encode a video with a given CRF | `<name>_compressed.mp4` |
| `to_mp4` | Convert a video to `.mp4` | `<name>.mp4` |
| `audio_extract` | Extract the audio track as `.mp3` | `<name>.mp3` |
| `audio_eliminate` | Remove the audio track | `<name>_wo_audio.mp4` |
| `gui` | Launch the Tkinter GUI | – |

Both interfaces show conversion progress, which is read from FFmpeg through its
`-progress` option over a local TCP connection (tqdm on the CLI, a progress bar
widget in the GUI).

## Requirements

- Python 3.12
- FFmpeg on your `PATH` (`ffmpeg-python` is only a wrapper and does not bundle it)

## Install dependencies

For Windows 11:

```powershell
# Install command
winget install astral-sh.uv Gyan.FFmpeg

# Install dependencies
uv sync

# GUI executable creation (PyInstaller lives in the optional `build` extra)
uv sync --extra build
uv run pyinstaller .\src\video_converter\gui.py --onefile --noconsole
```

## How to use

After installation the `video-converter` command is also available, so
`video-converter gui` behaves the same as the module form below.

```powershell
# Open GUI
python -m video_converter gui

# Compress video (lower crf means higher quality; defaults to 23)
python -m video_converter compress input.mp4 --crf 23

# Convert video to mp4
python -m video_converter to_mp4 input.mov

# Eliminate audio from video
python -m video_converter audio_eliminate input.mp4

# Extract audio from video
python -m video_converter audio_extract input.mp4

# Show available options
python -m video_converter --help
```

`output_path` is optional for every command. When omitted, the output is written
next to the input file using the naming rules in the table above.

An existing output file is overwritten without asking. If the resolved output
would be the same file as the input (for example `to_mp4 input.mp4` with no
`output_path`), the command stops with a `ValueError` instead of destroying the
input.

## How to develop

```bash
uv sync --dev
pre-commit install

# optional
pre-commit run --all-files
```

Common tasks are available through the `Makefile`:

```bash
make lint    # ruff check + format check
make test    # pytest
make html    # build the Sphinx docs into docs/sphinx/build/html
make livehtml  # auto-rebuild and serve the docs
make check   # lint + test + html
```

The test suite downloads a small sample video into `tests/` on first run, and
requires FFmpeg to be installed. `tests/test_gui.py` opens a real Tk window and
is skipped automatically when no display or usable Tcl/Tk is available.

`ruff` and `pytest` run in CI through the `ci` workflow on every push and pull
request.

## Documentation

The documentation is built with Sphinx from `docs/sphinx/` and published to
GitHub Pages by the `docs` workflow on every push to `main`.

## License

[MIT](LICENSE)
