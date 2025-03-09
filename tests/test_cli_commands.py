import urllib.request
from pathlib import Path

import ffmpeg
import pytest

from video_converter import progress
from video_converter.compressor import compress
from video_converter.conveter import to_mp4
from video_converter.extractor import audio_eliminate, audio_extract


@pytest.fixture
def test_video_path():
    """テスト用の動画ファイルのパス"""
    test_video_path = Path(__file__).parent / "car-detection.mp4"
    if not test_video_path.exists():
        print(f"{test_video_path} が存在しないため、ダウンロードします...")
        url = "https://github.com/intel-iot-devkit/sample-videos/raw/refs/heads/master/car-detection.mp4"
        urllib.request.urlretrieve(url, str(test_video_path))
        print(f"{test_video_path} をダウンロードしました")
    assert test_video_path.exists(), f"{test_video_path} が存在しません。ダウンロードに失敗した可能性があります。"
    return test_video_path


@pytest.fixture
def output_dir():
    """出力ファイルのパスを設定"""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture
def compressed_path(output_dir):
    """圧縮された動画ファイルのパス"""
    return output_dir / "car-detection_compressed.mp4"


@pytest.fixture
def mp4_path(output_dir):
    """MP4動画ファイルのパス"""
    return output_dir / "car-detection.mp4"


@pytest.fixture
def mp3_path(output_dir):
    """MP3音声ファイルのパス"""
    return output_dir / "car-detection.mp3"


@pytest.fixture
def no_audio_path(output_dir):
    """音声なし動画ファイルのパス"""
    return output_dir / "car-detection_wo_audio.mp4"


@pytest.fixture(autouse=True)
def cleanup(output_dir, compressed_path, mp4_path, mp3_path, no_audio_path):
    """テスト前後のクリーンアップ"""
    # 既存の出力ファイルを削除
    for path in [compressed_path, mp4_path, mp3_path, no_audio_path]:
        if path.exists():
            path.unlink()

    yield

    # テスト終了後に出力ファイルを削除
    for path in [compressed_path, mp4_path, mp3_path, no_audio_path]:
        if path.exists():
            path.unlink()

    # 出力ディレクトリを削除
    if output_dir.exists():
        output_dir.rmdir()


def test_compress(test_video_path, compressed_path):
    """動画圧縮機能のテスト"""
    # 圧縮パイプラインを作成
    pipeline = compress(test_video_path, compressed_path)

    # パイプラインを実行
    result = progress.run_with_tcp_pbar(str(test_video_path), pipeline)

    # 出力ファイルが存在することを確認
    assert compressed_path.exists(), f"{compressed_path} が作成されませんでした"

    # 出力ファイルが有効な動画ファイルであることを確認
    probe = ffmpeg.probe(str(compressed_path))
    assert "streams" in probe, "出力ファイルが有効な動画ファイルではありません"

    # 動画ストリームが存在することを確認
    video_streams = [s for s in probe["streams"] if s["codec_type"] == "video"]
    assert len(video_streams) > 0, "出力ファイルに動画ストリームがありません"


def test_to_mp4(test_video_path, mp4_path):
    """MP4変換機能のテスト"""
    # MP4変換パイプラインを作成
    pipeline = to_mp4(test_video_path, str(mp4_path))

    # パイプラインを実行
    result = progress.run_with_tcp_pbar(str(test_video_path), pipeline)

    # 出力ファイルが存在することを確認
    assert mp4_path.exists(), f"{mp4_path} が作成されませんでした"

    # 出力ファイルが有効な動画ファイルであることを確認
    probe = ffmpeg.probe(str(mp4_path))
    assert "streams" in probe, "出力ファイルが有効な動画ファイルではありません"

    # 動画ストリームが存在することを確認
    video_streams = [s for s in probe["streams"] if s["codec_type"] == "video"]
    assert len(video_streams) > 0, "出力ファイルに動画ストリームがありません"


def test_audio_extract(test_video_path, mp3_path):
    """音声抽出機能のテスト"""
    # 音声抽出パイプラインを作成
    pipeline = audio_extract(test_video_path, str(mp3_path))

    # パイプラインを実行
    result = progress.run_with_tcp_pbar(str(test_video_path), pipeline)

    # 出力ファイルが存在することを確認
    assert mp3_path.exists(), f"{mp3_path} が作成されませんでした"

    # 出力ファイルが有効な音声ファイルであることを確認
    probe = ffmpeg.probe(str(mp3_path))
    assert "streams" in probe, "出力ファイルが有効な音声ファイルではありません"

    # 音声ストリームが存在することを確認
    audio_streams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
    assert len(audio_streams) > 0, "出力ファイルに音声ストリームがありません"


def test_audio_eliminate(test_video_path, no_audio_path):
    """音声削除機能のテスト"""
    # 音声削除パイプラインを作成
    pipeline = audio_eliminate(test_video_path, str(no_audio_path))

    # パイプラインを実行
    result = progress.run_with_tcp_pbar(str(test_video_path), pipeline)

    # 出力ファイルが存在することを確認
    assert no_audio_path.exists(), f"{no_audio_path} が作成されませんでした"

    # 出力ファイルが有効な動画ファイルであることを確認
    probe = ffmpeg.probe(str(no_audio_path))
    assert "streams" in probe, "出力ファイルが有効な動画ファイルではありません"

    # 動画ストリームが存在することを確認
    video_streams = [s for s in probe["streams"] if s["codec_type"] == "video"]
    assert len(video_streams) > 0, "出力ファイルに動画ストリームがありません"

    # 音声ストリームが存在しないことを確認
    audio_streams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
    assert len(audio_streams) == 0, "出力ファイルに音声ストリームが残っています"
