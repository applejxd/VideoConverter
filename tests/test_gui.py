import subprocess
import sys

import pytest

pytest.importorskip("tkinter")

#: GUI を生成できるかを別プロセスで確認するためのコード。
#: tkinterdnd2 は環境によっては Xlib のアサーション失敗で SIGABRT を送出し、
#: プロセスごと落とす。これは Python の例外として捕捉できないため、
#: 判定は必ず別プロセスで行う。
_PROBE = "from tkinterdnd2 import TkinterDnD; TkinterDnD.Tk().destroy()"


def _gui_available() -> bool:
    """ドラッグ&ドロップ対応のウィンドウを生成できる環境かを判定する。

    :return: 生成できる場合は ``True``。
    """
    try:
        completed = subprocess.run(
            [sys.executable, "-c", _PROBE],
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


requires_gui = pytest.mark.skipif(
    not _gui_available(),
    reason=(
        "GUI を生成できない環境 (ディスプレイ、Tcl/Tk、または tkdnd が利用できない)"
    ),
)


@requires_gui
def test_gui_creation():
    """ウィンドウが生成でき、破棄時に sys.stdout が復元されることを確認する。

    mainloop() は呼ばない。conftest.py の monkey.patch_all() により
    threading は greenlet 化されており、mainloop() のようにハブへ制御を
    返さないブロッキング呼び出しを別スレッドで動かすと
    join(timeout=...) が機能しないため。
    """
    from video_converter.gui import create_window

    original_stdout = sys.stdout
    window = create_window()
    try:
        assert window.root is not None
        # 保留中のイベントを処理し、ウィジェットが実際に配置できることを確認する
        window.root.update()
        assert sys.stdout is not original_stdout, (
            "コンソールへの sys.stdout 差し替えが行われていません"
        )
    finally:
        window.root.destroy()
        window.root.update()

    assert sys.stdout is original_stdout, (
        "ウィンドウ破棄後に sys.stdout が復元されていません"
    )
