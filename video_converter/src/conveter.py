import os
import sys

import ffmpeg

from video_converter.src import progress


def to_mp4(path: str) -> None:
    """.mp4 へ変換

    :param path: 動画のファイルパス
    """
    mp4_path = f"{os.path.splitext(path)[0]}.mp4"
    pipeline = ffmpeg.input(path).output(mp4_path)
    return pipeline
