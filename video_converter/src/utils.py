from functools import wraps

from video_converter.src import progress


def cli_wrapper(func):
    # cf. https://qiita.com/moonwalkerpoday/items/9bd987667a860adf80a2
    @wraps(func)
    def wrapper(path, *args, **kwargs):
        pipeline = func(path, *args, **kwargs)
        progress.run_with_tcp_pbar(path, pipeline)

    return wrapper
