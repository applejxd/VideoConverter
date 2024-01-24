import os

import ffmpeg


def audio_extract(path: str) -> None:
    """音声を .mp3 で抽出

    :param path: 動画のファイルパス
    """
    audio_path = f"{os.path.splitext(path)[0]}.mp3"
    ffmpeg.input(path).output(audio_path).run()


def audio_eliminate(path: str) -> None:
    """音声を削除

    :param path: 動画のファイルパス
    """
    no_audio_path = f"{os.path.splitext(path)[0]}_wo_audio.mp4"
    ffmpeg.input(path).output(no_audio_path, streams="a").run()
