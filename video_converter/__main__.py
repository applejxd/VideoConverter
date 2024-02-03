"""
For library call
$ python video_converter --help
"""

from functools import wraps

from fire import Fire
from tqdm import tqdm

from video_converter.gui import open_window
from video_converter.src import progress
from video_converter.src.compressor import compress
from video_converter.src.conveter import to_mp4
from video_converter.src.extractor import audio_eliminate, audio_extract


def cli_wrapper(func):
    # cf. https://qiita.com/moonwalkerpoday/items/9bd987667a860adf80a2
    @wraps(func)
    def wrapper(path, *args, **kwargs):
        pipeline = func(path, *args, **kwargs)
        progress.run_with_tcp_pbar(path, pipeline)

    return wrapper


Fire(
    {
        "gui": open_window,
        "compress": cli_wrapper(compress),
        "to_mp4": cli_wrapper(to_mp4),
        "audio_eliminate": cli_wrapper(audio_eliminate),
        "audio_extract": cli_wrapper(audio_extract),
    }
)
