"""入出力パスの解決と、変換失敗時の振る舞いに関する回帰テスト。"""

import ffmpeg
import pytest

from video_converter import progress
from video_converter.compressor import compress
from video_converter.converter import to_mp4
from video_converter.extractor import audio_eliminate, audio_extract


@pytest.mark.parametrize(
    ("func", "suffix"),
    [
        (to_mp4, ".mp4"),
        (audio_extract, ".mp3"),
    ],
)
def test_same_input_and_output_is_rejected(tmp_path, test_video_path, func, suffix):
    """既定の出力先が入力と同一になる場合はエラーになる。

    FFmpeg は同じファイルを読み書きできないため、実行前に停止する必要がある。
    """
    same_suffix_input = tmp_path / f"sample{suffix}"
    same_suffix_input.write_bytes(test_video_path.read_bytes())

    with pytest.raises(ValueError, match="入力と出力が同じファイル"):
        func(same_suffix_input)


def test_explicit_output_equal_to_input_is_rejected(test_video_path):
    """output_path に入力と同じパスを明示した場合もエラーになる。"""
    with pytest.raises(ValueError, match="入力と出力が同じファイル"):
        compress(test_video_path, test_video_path)


def test_missing_input_raises_file_not_found(tmp_path):
    """入力ファイルが存在しない場合は FileNotFoundError になる。"""
    with pytest.raises(FileNotFoundError):
        audio_eliminate(tmp_path / "not-exist.mp4")


def test_existing_output_is_overwritten(tmp_path, test_video_path):
    """出力先が既に存在しても、上書きして変換が完了する。

    overwrite_output() が無いと FFmpeg が "Overwrite? [y/N]" で停止し、
    進捗待ちの accept() が解放されずに破綻する。
    """
    output_path = tmp_path / "already-there.mp4"
    output_path.write_bytes(b"stale content")
    stale_size = output_path.stat().st_size

    pipeline = to_mp4(test_video_path, str(output_path))
    progress.run_with_tcp_pbar(str(test_video_path), pipeline)

    assert output_path.stat().st_size != stale_size, "出力が上書きされていません"
    probe = ffmpeg.probe(str(output_path))
    assert any(s["codec_type"] == "video" for s in probe["streams"])


def test_ffmpeg_failure_raises_instead_of_hanging(tmp_path, test_video_path):
    """FFmpeg が接続前に失敗した場合、ハングせず例外になる。

    accept() のタイムアウトと link_exception が無いと、進捗側の greenlet が
    解放されずハングするか LoopExit で落ちる。
    """
    unwritable_output = tmp_path / "no-such-dir" / "out.mp4"

    pipeline = to_mp4(test_video_path, str(unwritable_output))
    with pytest.raises(ffmpeg.Error):
        progress.run_with_tcp_pbar(str(test_video_path), pipeline)
