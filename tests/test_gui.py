import queue
import threading

import pytest

tkinter = pytest.importorskip("tkinter")


def _tk_available() -> bool:
    """Tk のウィンドウを生成できる環境かどうかを判定する。

    :return: 生成できる場合は ``True``。
    """
    try:
        root = tkinter.Tk()
    except tkinter.TclError:
        return False
    root.destroy()
    return True


requires_tk = pytest.mark.skipif(
    not _tk_available(),
    reason="Tk のウィンドウを生成できない環境 (ディスプレイまたは Tcl/Tk が無い)",
)


@requires_tk
def test_gui_creation():
    """GUIが正常に作成されるかテスト"""
    from video_converter.gui import create_window

    errors: queue.Queue[BaseException] = queue.Queue()

    # GUIをスレッドで起動（メインスレッドをブロックしないため）
    def run_gui():
        try:
            window = create_window()
            # 短時間だけGUIを表示してから閉じる
            window.root.after(1000, window.root.destroy)
            window.root.mainloop()
        except BaseException as exc:  # noqa: BLE001
            errors.put(exc)

    # GUIスレッドを起動
    gui_thread = threading.Thread(target=run_gui)
    # デーモンスレッドとして起動（メインスレッド終了時に自動終了）
    gui_thread.daemon = True
    gui_thread.start()

    # スレッドが終了するまで待機（最大5秒）
    gui_thread.join(timeout=5)

    # スレッド内で例外が出ていないことを確認する。
    # is_alive() だけを見ると、例外で死んだ場合も「正常終了」と誤判定する
    if not errors.empty():
        raise AssertionError(f"GUI スレッドで例外が発生しました: {errors.get()}")

    # スレッドが正常に終了したことを確認
    assert not gui_thread.is_alive(), "GUIスレッドが正常に終了しませんでした"
