import threading
from pathlib import Path

import pytest

from video_converter.gui import create_window


@pytest.fixture
def test_video_path():
    """テスト用の動画ファイルのパス"""
    test_video_path = Path(__file__).parent / "car-detection.mp4"
    assert test_video_path.exists(), f"{test_video_path} が存在しません"
    return test_video_path


def test_gui_creation(test_video_path):
    """GUIが正常に作成されるかテスト"""

    # GUIをスレッドで起動（メインスレッドをブロックしないため）
    def run_gui():
        window = create_window()
        # 短時間だけGUIを表示してから閉じる
        window.root.after(1000, window.root.destroy)
        window.root.mainloop()

    # GUIスレッドを起動
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.daemon = (
        True  # デーモンスレッドとして起動（メインスレッド終了時に自動終了）
    )
    gui_thread.start()

    # スレッドが終了するまで待機（最大5秒）
    gui_thread.join(timeout=5)

    # スレッドが正常に終了したことを確認
    assert not gui_thread.is_alive(), "GUIスレッドが正常に終了しませんでした"
