"""入出力パスの解決を担うモジュール。

各変換関数が共通で行う「入力の存在確認」「出力先の既定値の決定」
「入力と出力が同一になっていないかの確認」をまとめる。

``progress`` や ``gevent`` に依存しないため、パス解決のためだけに
モジュールを import しても副作用が発生しない。
"""

import os
from pathlib import Path


def resolve_io_paths(
    input_path: str | os.PathLike,
    output_path: str | os.PathLike,
    default_suffix: str,
    default_stem_suffix: str = "",
) -> tuple[Path, Path]:
    """入力パスを検証し、出力パスを確定する。

    ``output_path`` が空文字の場合は、入力と同じディレクトリに
    ``<入力のファイル名><default_stem_suffix><default_suffix>`` を作る。

    :param input_path: 入力する動画のファイルパス。
    :param output_path: 出力先のファイルパス。空文字の場合は既定値を用いる。
    :param default_suffix: 既定の出力先に使う拡張子 (``".mp4"`` など)。
    :param default_stem_suffix: 既定の出力先のファイル名に付ける接尾辞
        (``"_compressed"`` など)。
    :return: (入力パス, 出力パス) のタプル。
    :raises FileNotFoundError: 入力パスがファイルとして存在しない場合。
    :raises ValueError: 入力パスと出力パスが同一のファイルを指す場合。
        FFmpeg は同じファイルを読み書きできず、変換を実行すると入力を
        破壊するため、事前に停止する。
    """
    input_path = Path(input_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"{input_path} が見つかりません")

    if str(output_path) == "":
        output_path = (
            input_path.parent
            / f"{input_path.stem}{default_stem_suffix}{default_suffix}"
        )
    else:
        output_path = Path(output_path)

    if _is_same_file(input_path, output_path):
        raise ValueError(
            f"入力と出力が同じファイル ({input_path}) を指しています。"
            " output_path に別のパスを指定してください"
        )

    return input_path, output_path


def _is_same_file(input_path: Path, output_path: Path) -> bool:
    """2 つのパスが同一のファイルを指すかどうかを判定する。

    出力先がまだ存在しない場合は ``os.path.samefile`` を使えないため、
    正規化した絶対パスを比較する。

    :param input_path: 入力パス。
    :param output_path: 出力パス。
    :return: 同一のファイルを指す場合は ``True``。
    """
    if output_path.exists():
        return os.path.samefile(input_path, output_path)
    return input_path.resolve() == output_path.resolve()
