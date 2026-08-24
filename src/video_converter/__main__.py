"""CLI エントリポイント。

.. code-block:: console

   $ python -m video_converter --help

``gevent`` の monkey patch は、他のモジュールが ``ssl`` や ``socket`` を
import するより先に適用する必要がある。そのためライブラリ側ではなく
このエントリポイントの先頭で実行する。
"""

from gevent import monkey

monkey.patch_all()

from fire import Fire  # noqa: E402

from video_converter.compressor import compress  # noqa: E402
from video_converter.converter import to_mp4  # noqa: E402
from video_converter.extractor import audio_eliminate, audio_extract  # noqa: E402
from video_converter.gui import open_window  # noqa: E402
from video_converter.utils import cli_wrapper  # noqa: E402


def main() -> None:
    """Fire でサブコマンドを解決し、CLI を実行する。"""
    Fire(
        {
            "gui": open_window,
            "compress": cli_wrapper(compress),
            "to_mp4": cli_wrapper(to_mp4),
            "audio_eliminate": cli_wrapper(audio_eliminate),
            "audio_extract": cli_wrapper(audio_extract),
        }
    )


if __name__ == "__main__":
    main()
