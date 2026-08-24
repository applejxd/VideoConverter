"""ffmpeg-python を用いた動画変換ライブラリ。

CLI (Fire) と GUI (Tkinter) の 2 つのインターフェースから、動画の圧縮・
形式変換・音声抽出・音声除去を行う。

各変換関数は ffmpeg を即座に実行せず、``ffmpeg.nodes.Node`` (pipeline) を
組み立てて返す。実行は :func:`video_converter.progress.run_with_tcp_pbar` が
担当し、その際 FFmpeg の ``-progress`` オプションによる進捗を TCP 経由で
受け取ってプログレスバーへ反映する。

モジュール構成:

- :mod:`video_converter.compressor` -- 動画の圧縮 (CRF 指定)
- :mod:`video_converter.converter` -- .mp4 への形式変換
- :mod:`video_converter.extractor` -- 音声の抽出および除去
- :mod:`video_converter.progress` -- TCP 経由の進捗取得と pipeline 実行
- :mod:`video_converter.gui` -- Tkinter による GUI
- :mod:`video_converter.utils` -- CLI 用のデコレータ
"""

from video_converter.compressor import compress
from video_converter.converter import to_mp4
from video_converter.extractor import audio_eliminate, audio_extract

__all__ = [
    "audio_eliminate",
    "audio_extract",
    "compress",
    "to_mp4",
]
