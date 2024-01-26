import os
import sys

import ffmpeg

from video_converter.src import progress


def to_mp4(path: str) -> None:
    """.mp4 へ変換

    :param path: 動画のファイルパス
    """
    mp4_path = f"{os.path.splitext(path)[0]}.mp4"

    try:
        ffmpeg.input(path).output(mp4_path).global_args(
            "-progress", f"tcp://127.0.0.1:{progress.PORT}"
        ).run()
    except ffmpeg.Error as e:
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
