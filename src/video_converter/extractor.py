import os
from pathlib import Path

import ffmpeg


def audio_extract(
    input_path: str | os.PathLike, output_path: str = ""
) -> ffmpeg.nodes.Node:
    """音声を .mp3 で抽出

    :param input_path: 動画のファイルパス
    :param output_path: 出力ファイルパス (省略した場合は、元のファイル名に".mp3"を付加)
    :return: 音声を .mp3 で抽出するパイプライン
    """
    input_path = Path(input_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"{input_path} が見つかりません")

    if output_path == "":
        output_path = input_path.parent / f"{input_path.stem}.mp3"
    else:
        output_path = Path(output_path)
    pipeline = ffmpeg.input(str(input_path)).output(str(output_path))
    return pipeline


def audio_eliminate(
    input_path: str | os.PathLike, output_path: str = ""
) -> ffmpeg.nodes.Node:
    """音声を削除

    :param input_path: 動画のファイルパス
    :param output_path: 出力ファイルパス (省略した場合は、元のファイル名に"_wo_audio.mp4"を付加)
    :return: 音声を削除するパイプライン
    """
    input_path = Path(input_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"{input_path} が見つかりません")

    if output_path == "":
        output_path = input_path.parent / f"{input_path.stem}_wo_audio.mp4"
    else:
        output_path = Path(output_path)

    pipeline = ffmpeg.input(str(input_path)).output(str(output_path), **{"an": None})
    return pipeline
