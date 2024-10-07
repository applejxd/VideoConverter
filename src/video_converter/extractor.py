from pathlib import Path
from typing import Union

import ffmpeg

PathLike = Union[str, Path]


def audio_extract(path: PathLike) -> None:
    """音声を .mp3 で抽出

    :param path: 動画のファイルパス
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"{path} が見つかりません")

    audio_path = path.parent / f"{path.stem}.mp3"
    pipeline = ffmpeg.input(str(path)).output(str(audio_path))
    return pipeline


def audio_eliminate(path: PathLike) -> None:
    """音声を削除

    :param path: 動画のファイルパス
    :param path:
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"{path} が見つかりません")

    no_audio_path = path.parent / f"{path.stem}_wo_audio.mp4"
    pipeline = ffmpeg.input(str(path)).output(path(no_audio_path)).global_args("-an")
    return pipeline
