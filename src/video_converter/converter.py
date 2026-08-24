"""動画の形式を変換するモジュール。

現状は .mp4 への変換のみを提供する。
"""

import os

import ffmpeg

from video_converter.paths import resolve_io_paths


def to_mp4(input_path: str | os.PathLike, output_path: str = "") -> ffmpeg.nodes.Node:
    """.mp4 へ変換

    :param input_path: 動画のファイルパス
    :param output_path: 出力ファイルパス (省略した場合は、元のファイル名に".mp4"を付加)
    :return: .mp4 へ変換するパイプライン。出力先が既に存在する場合は上書きする
    :raises FileNotFoundError: 入力パスがファイルとして存在しない場合
    :raises ValueError: 入力パスと出力パスが同一のファイルを指す場合
        (拡張子が .mp4 の入力に対し output_path を省略した場合など)
    """
    input_path, output_path = resolve_io_paths(
        input_path, output_path, default_suffix=".mp4"
    )

    pipeline = ffmpeg.input(str(input_path)).output(str(output_path)).overwrite_output()
    return pipeline
