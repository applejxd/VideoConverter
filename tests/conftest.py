"""pytest の共通設定とフィクスチャ。

``video_converter.progress`` は gevent の monkey patch を前提とする。
テストは :mod:`video_converter.__main__` を経由しないため、
他のモジュールが ``ssl`` や ``socket`` を import するより先に、
ここで patch を適用する。
"""

from gevent import monkey

monkey.patch_all()

import urllib.request  # noqa: E402
from pathlib import Path  # noqa: E402

import pytest  # noqa: E402

#: 変換テストに使うサンプル動画の取得元。
SAMPLE_VIDEO_URL = (
    "https://github.com/intel-iot-devkit/sample-videos/raw/refs/heads/master/"
    "car-detection.mp4"
)


@pytest.fixture(scope="session")
def test_video_path() -> Path:
    """テスト用の動画ファイルのパス。

    リポジトリには動画を含めないため、存在しない場合はダウンロードする。

    :return: サンプル動画のパス。
    """
    video_path = Path(__file__).parent / "car-detection.mp4"
    if not video_path.exists():
        print(f"{video_path} が存在しないため、ダウンロードします...")
        urllib.request.urlretrieve(SAMPLE_VIDEO_URL, str(video_path))
        print(f"{video_path} をダウンロードしました")
    assert video_path.exists(), (
        f"{video_path} が存在しません。ダウンロードに失敗した可能性があります。"
    )
    return video_path
