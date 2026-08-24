"""動画を圧縮するモジュール。

ffmpeg の CRF (Constant Rate Factor) を指定して動画を再エンコードする。
"""

import os

import ffmpeg

from video_converter.paths import resolve_io_paths


def compress(
    input_path: str | os.PathLike,
    output_path: str | os.PathLike = "",
    crf: int = 23,
) -> ffmpeg.nodes.Node:
    """動画を圧縮

    :param input_path: 動画のファイルパス
    :param output_path: 圧縮後の動画のファイルパス (省略した場合は、元のファイル名に"_compressed"を付加)
    :param crf: 圧縮後の動画品質 (低いほうが品質が高い)
    :return: 圧縮後の動画のパイプライン。出力先が既に存在する場合は上書きする
    :raises FileNotFoundError: 入力パスがファイルとして存在しない場合
    :raises ValueError: 入力パスと出力パスが同一のファイルを指す場合
    """
    input_path, output_path = resolve_io_paths(
        input_path,
        output_path,
        default_suffix=".mp4",
        default_stem_suffix="_compressed",
    )

    # Adjust the `crf` value for video quality (lower value means higher quality)
    pipeline = (
        ffmpeg.input(str(input_path))
        .output(str(output_path), crf=crf)
        .overwrite_output()
    )
    return pipeline
