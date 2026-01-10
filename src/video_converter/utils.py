from functools import wraps
from typing import Any, Callable

from video_converter import progress


def cli_wrapper(func: Callable) -> Callable:
    """CLIラッパーで進捗バーを表示するデコレータ.
    see https://qiita.com/moonwalkerpoday/items/9bd987667a860adf80a2.

    :param func: ラップする対象の関数
    :return: ラップされた関数
    """

    @wraps(func)
    def wrapper(path: str, *args: Any, **kwargs: Any) -> Any:
        """ラッピングされた関数

        :param path: 処理対象のパス
        :param args: その他の引数

        :param kwargs: キーワード引数
        :return: パイプラインの結果
        """
        pipeline = func(path, *args, **kwargs)
        return progress.run_with_tcp_pbar(path, pipeline)

    return wrapper
