from pathlib import Path
from typing import Optional, Union

import ffmpeg

PathLike = Union[str, Path]


def compress(path: PathLike, crf: Optional[int] = 23) -> None:
    """動画を圧縮

    :param path: 動画のファイルパス
    :param crf: 圧縮後の動画品質 (低いほうが品質が高い)
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"{path} が見つかりません")

    compressed_path = path.parent / f"{path.stem}_compressed.mp4"

    # Adjust the `crf` value for video quality (lower value means higher quality)
    pipeline = ffmpeg.input(str(path)).output(str(compressed_path), crf=crf)
    return pipeline
