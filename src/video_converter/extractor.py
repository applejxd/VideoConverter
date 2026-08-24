"""動画から音声を抽出・除去するモジュール。"""

import os

import ffmpeg

from video_converter.paths import resolve_io_paths


def audio_extract(
    input_path: str | os.PathLike, output_path: str = ""
) -> ffmpeg.nodes.Node:
    """音声を .mp3 で抽出

    :param input_path: 動画のファイルパス
    :param output_path: 出力ファイルパス (省略した場合は、元のファイル名に".mp3"を付加)
    :return: 音声を .mp3 で抽出するパイプライン。出力先が既に存在する場合は上書きする
    :raises FileNotFoundError: 入力パスがファイルとして存在しない場合
    :raises ValueError: 入力パスと出力パスが同一のファイルを指す場合
    """
    input_path, output_path = resolve_io_paths(
        input_path, output_path, default_suffix=".mp3"
    )

    pipeline = ffmpeg.input(str(input_path)).output(str(output_path)).overwrite_output()
    return pipeline


def audio_eliminate(
    input_path: str | os.PathLike, output_path: str = ""
) -> ffmpeg.nodes.Node:
    """音声を削除

    :param input_path: 動画のファイルパス
    :param output_path: 出力ファイルパス
        (省略した場合は、元のファイル名に"_wo_audio.mp4"を付加)
    :return: 音声を削除するパイプライン。出力先が既に存在する場合は上書きする
    :raises FileNotFoundError: 入力パスがファイルとして存在しない場合
    :raises ValueError: 入力パスと出力パスが同一のファイルを指す場合
    """
    input_path, output_path = resolve_io_paths(
        input_path,
        output_path,
        default_suffix=".mp4",
        default_stem_suffix="_wo_audio",
    )

    pipeline = (
        ffmpeg.input(str(input_path))
        .output(str(output_path), **{"an": None})
        .overwrite_output()
    )
    return pipeline
