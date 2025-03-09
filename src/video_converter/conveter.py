import os
from pathlib import Path

import ffmpeg


def to_mp4(input_path: str | os.PathLike, output_path: str = "") -> ffmpeg.nodes.Node:
    """.mp4 へ変換

    :param input_path: 動画のファイルパス
    :param output_path: 出力ファイルパス (省略した場合は、元のファイル名に".mp4"を付加)
    :return: .mp4 へ変換するパイプライン
    """
    input_path = Path(input_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"{input_path} が見つかりません")

    if output_path == "":
        output_path = input_path.parent / f"{input_path.stem}.mp4"
    else:
        output_path = Path(output_path)

    pipeline = ffmpeg.input(str(input_path)).output(str(output_path))
    return pipeline
