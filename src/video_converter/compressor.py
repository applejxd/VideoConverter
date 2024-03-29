import os
import sys
from typing import Optional

import ffmpeg

from video_converter import progress


def compress(path: str, crf: Optional[int] = 23) -> None:
    """動画を圧縮

    :param path: 動画のファイルパス
    :param crf: 圧縮後の動画品質 (低いほうが品質が高い)
    """
    compressed_path = f"{os.path.splitext(path)[0]}_compressed.mp4"

    # Adjust the `crf` value for video quality (lower value means higher quality)
    pipeline = ffmpeg.input(path).output(compressed_path, crf=crf)

    return pipeline
