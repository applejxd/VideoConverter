import os
from pathlib import Path
from typing import Optional

import ffmpeg


def compress(
    input_path: str | os.PathLike,
    output_path: str | os.PathLike = "",
    crf: Optional[int] = 23,
) -> ffmpeg.nodes.Node:
    """動画を圧縮

    :param input_path: 動画のファイルパス
    :param output_path: 圧縮後の動画のファイルパス (省略した場合は、元のファイル名に"_compressed"を付加)
    :param crf: 圧縮後の動画品質 (低いほうが品質が高い)
    :return: 圧縮後の動画のパイプライン
    """
    input_path = Path(input_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"{input_path} が見つかりません")

    if output_path == "":
        output_path = input_path.parent / f"{input_path.stem}_compressed.mp4"
    else:
        output_path = Path(output_path)

    # Adjust the `crf` value for video quality (lower value means higher quality)
    pipeline = ffmpeg.input(str(input_path)).output(str(output_path), crf=crf)
    return pipeline
