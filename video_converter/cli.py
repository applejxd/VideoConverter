from fire import Fire as _Fire

from video_converter.gui import open_window
from video_converter.src.compressor import compress
from video_converter.src.conveter import to_mp4
from video_converter.src.extractor import audio_eliminate, audio_extract

_Fire()
