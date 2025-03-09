import threading
import time
import tkinter as tk
import unittest
from pathlib import Path

from video_converter.gui import create_window


class TestGUI(unittest.TestCase):
    """GUIの基本機能テスト"""

    def setUp(self):
        """テスト前の準備"""
        # テスト用の動画ファイルのパス
        self.test_video_path = Path(__file__).parent / "car-detection.mp4"
        self.assertTrue(self.test_video_path.exists(), f"{self.test_video_path} が存在しません")

    def test_gui_creation(self):
        """GUIが正常に作成されるかテスト"""
        # GUIをスレッドで起動（メインスレッドをブロックしないため）
        def run_gui():
            window = create_window()
            # 短時間だけGUIを表示してから閉じる
            window.root.after(1000, window.root.destroy)
            window.root.mainloop()
        
        # GUIスレッドを起動
        gui_thread = threading.Thread(target=run_gui)
        gui_thread.daemon = True  # デーモンスレッドとして起動（メインスレッド終了時に自動終了）
        gui_thread.start()
        
        # スレッドが終了するまで待機（最大5秒）
        gui_thread.join(timeout=5)
        
        # スレッドが正常に終了したことを確認
        self.assertFalse(gui_thread.is_alive(), "GUIスレッドが正常に終了しませんでした")


if __name__ == "__main__":
    unittest.main()
