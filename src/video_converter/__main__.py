"""
For library call
$ python video_converter --help
"""

from fire import Fire

from video_converter.compressor import compress
from video_converter.conveter import to_mp4
from video_converter.extractor import audio_eliminate, audio_extract
from video_converter.gui import open_window
from video_converter.utils import cli_wrapper

Fire(
    {
        "gui": open_window,
        "compress": cli_wrapper(compress),
        "to_mp4": cli_wrapper(to_mp4),
        "audio_eliminate": cli_wrapper(audio_eliminate),
        "audio_extract": cli_wrapper(audio_extract),
    }
)
