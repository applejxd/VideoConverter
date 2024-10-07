from pathlib import Path
from typing import Union

import ffmpeg

PathLike = Union[str, Path]


def to_mp4(path: PathLike) -> None:
    """.mp4 へ変換

    :param path: 動画のファイルパス
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"{path} が見つかりません")

    mp4_path = path.parent / f"{path.stem}.mp4"

    pipeline = ffmpeg.input(str(path)).output(str(mp4_path))
    return pipeline
