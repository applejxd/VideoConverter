import os
import sys

import ffmpeg

from video_converter import progress


def audio_extract(path: str) -> None:
    """音声を .mp3 で抽出

    :param path: 動画のファイルパス
    """
    audio_path = f"{os.path.splitext(path)[0]}.mp3"
    pipeline = ffmpeg.input(path).output(audio_path)
    return pipeline


def audio_eliminate(path: str) -> None:
    """音声を削除

    :param path: 動画のファイルパス
    :param path:
    """
    no_audio_path = f"{os.path.splitext(path)[0]}_wo_audio.mp4"
    pipeline = ffmpeg.input(path).output(no_audio_path).global_args("-an")
    return pipeline
