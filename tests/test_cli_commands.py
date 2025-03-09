import os
import unittest
from pathlib import Path

import ffmpeg

from video_converter import progress
from video_converter.compressor import compress
from video_converter.conveter import to_mp4
from video_converter.extractor import audio_eliminate, audio_extract


class TestCliCommands(unittest.TestCase):
    """Python-Fireに登録されている機能が正常終了するかテスト"""

    def setUp(self):
        """テスト前の準備"""
        # テスト用の動画ファイルのパス
        self.test_video_path = Path(__file__).parent / "car-detection.mp4"
        self.assertTrue(self.test_video_path.exists(), f"{self.test_video_path} が存在しません")
        
        # 出力ファイルのパスを設定
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # 出力ファイルのパス
        self.compressed_path = self.output_dir / "car-detection_compressed.mp4"
        self.mp4_path = self.output_dir / "car-detection.mp4"
        self.mp3_path = self.output_dir / "car-detection.mp3"
        self.no_audio_path = self.output_dir / "car-detection_wo_audio.mp4"
        
        # 既存の出力ファイルを削除
        for path in [self.compressed_path, self.mp4_path, self.mp3_path, self.no_audio_path]:
            if path.exists():
                path.unlink()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        # テスト終了後に出力ファイルを削除
        for path in [self.compressed_path, self.mp4_path, self.mp3_path, self.no_audio_path]:
            if path.exists():
                path.unlink()
        
        # 出力ディレクトリを削除
        if self.output_dir.exists():
            self.output_dir.rmdir()

    def test_compress(self):
        """動画圧縮機能のテスト"""
        # 圧縮パイプラインを作成
        pipeline = compress(self.test_video_path, self.compressed_path)
        
        # パイプラインを実行
        result = progress.run_with_tcp_pbar(str(self.test_video_path), pipeline)
        
        # 出力ファイルが存在することを確認
        self.assertTrue(self.compressed_path.exists(), f"{self.compressed_path} が作成されませんでした")
        
        # 出力ファイルが有効な動画ファイルであることを確認
        probe = ffmpeg.probe(str(self.compressed_path))
        self.assertIn("streams", probe, "出力ファイルが有効な動画ファイルではありません")
        
        # 動画ストリームが存在することを確認
        video_streams = [s for s in probe["streams"] if s["codec_type"] == "video"]
        self.assertGreater(len(video_streams), 0, "出力ファイルに動画ストリームがありません")

    def test_to_mp4(self):
        """MP4変換機能のテスト"""
        # MP4変換パイプラインを作成
        pipeline = to_mp4(self.test_video_path, str(self.mp4_path))
        
        # パイプラインを実行
        result = progress.run_with_tcp_pbar(str(self.test_video_path), pipeline)
        
        # 出力ファイルが存在することを確認
        self.assertTrue(self.mp4_path.exists(), f"{self.mp4_path} が作成されませんでした")
        
        # 出力ファイルが有効な動画ファイルであることを確認
        probe = ffmpeg.probe(str(self.mp4_path))
        self.assertIn("streams", probe, "出力ファイルが有効な動画ファイルではありません")
        
        # 動画ストリームが存在することを確認
        video_streams = [s for s in probe["streams"] if s["codec_type"] == "video"]
        self.assertGreater(len(video_streams), 0, "出力ファイルに動画ストリームがありません")

    def test_audio_extract(self):
        """音声抽出機能のテスト"""
        # 音声抽出パイプラインを作成
        pipeline = audio_extract(self.test_video_path, str(self.mp3_path))
        
        # パイプラインを実行
        result = progress.run_with_tcp_pbar(str(self.test_video_path), pipeline)
        
        # 出力ファイルが存在することを確認
        self.assertTrue(self.mp3_path.exists(), f"{self.mp3_path} が作成されませんでした")
        
        # 出力ファイルが有効な音声ファイルであることを確認
        probe = ffmpeg.probe(str(self.mp3_path))
        self.assertIn("streams", probe, "出力ファイルが有効な音声ファイルではありません")
        
        # 音声ストリームが存在することを確認
        audio_streams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
        self.assertGreater(len(audio_streams), 0, "出力ファイルに音声ストリームがありません")

    def test_audio_eliminate(self):
        """音声削除機能のテスト"""
        # 音声削除パイプラインを作成
        pipeline = audio_eliminate(self.test_video_path, str(self.no_audio_path))
        
        # パイプラインを実行
        result = progress.run_with_tcp_pbar(str(self.test_video_path), pipeline)
        
        # 出力ファイルが存在することを確認
        self.assertTrue(self.no_audio_path.exists(), f"{self.no_audio_path} が作成されませんでした")
        
        # 出力ファイルが有効な動画ファイルであることを確認
        probe = ffmpeg.probe(str(self.no_audio_path))
        self.assertIn("streams", probe, "出力ファイルが有効な動画ファイルではありません")
        
        # 動画ストリームが存在することを確認
        video_streams = [s for s in probe["streams"] if s["codec_type"] == "video"]
        self.assertGreater(len(video_streams), 0, "出力ファイルに動画ストリームがありません")
        
        # 音声ストリームが存在しないことを確認
        audio_streams = [s for s in probe["streams"] if s["codec_type"] == "audio"]
        self.assertEqual(len(audio_streams), 0, "出力ファイルに音声ストリームが残っています")


if __name__ == "__main__":
    unittest.main()
