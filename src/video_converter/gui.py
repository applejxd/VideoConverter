"""Tkinter による GUI インターフェース。

ウィンドウの構築は Builder パターン (:class:`WindowBuilder`) で行い、
ウィジェットへの参照は :class:`MyWindow` が保持する。変換の進捗は
:class:`video_converter.progress.FFmpegTCPSender` から
:class:`TkPBarWriter` のコールバックへ通知される (Observer パターン)。
"""

import sys
import time
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional

import ffmpeg
import gevent
from tkinterdnd2 import DND_FILES, TkinterDnD

from video_converter import progress
from video_converter.compressor import compress
from video_converter.converter import to_mp4
from video_converter.extractor import audio_eliminate, audio_extract
from video_converter.progress import FFmpegTCPSender

#: ラジオボタンの選択値と変換関数の対応表
METHODS = {
    "to_mp4": to_mp4,
    "audio_extract": audio_extract,
    "audio_eliminate": audio_eliminate,
    "compress": compress,
}


def _browse_file(string_var: tk.StringVar) -> None:
    """ファイル選択ダイアログを開き、選択されたパスを変数へ設定する。

    :param string_var: 選択されたファイルパスの格納先。
    """
    file_path = filedialog.askopenfilename()
    string_var.set(file_path)


def _drop_file(event: "tk.Event", string_var: tk.StringVar) -> None:
    """ドラッグ&ドロップされたファイルパスを変数へ設定する。

    tkinterdnd2 は Windows 形式のパスを ``{C:/path/to/file.mp4}`` のように
    波括弧で囲んで渡すため、それを取り除いてから格納する。

    :param event: ``<<Drop>>`` イベント。``data`` にファイルパスを含む。
    :param string_var: ドロップされたファイルパスの格納先。
    """
    # ドロップされたファイルパスを取得
    # Windows形式のパス（{C:/path/to/file.mp4}）から通常のパスに変換
    file_path = event.data.strip("{}")
    string_var.set(file_path)
    print(f"ファイルがドロップされました: {file_path}")


class StdoutRedirector:
    """標準出力を Tkinter のテキストウィジェットへ転送するクラス。

    :param text_widget: 出力先のテキストウィジェット。
    """

    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget

    def write(self, message: str) -> None:
        """メッセージをテキストウィジェットへ書き込む。

        :param message: 書き込む文字列。
        """
        self.text_widget.insert(tk.END, message)
        # テキストを最後にスクロール
        self.text_widget.see(tk.END)

    def flush(self) -> None:
        """``sys.stdout`` との互換性のために用意した何もしないメソッド。"""
        # flushメソッドを追加（sys.stdoutの互換性のため）
        pass


class MyWindow:
    """GUI のウィジェットおよび状態変数への参照を保持するコンテナ。

    各属性は :class:`WindowBuilder` の ``create_*`` メソッドによって設定され、
    生成前は ``None`` である。
    """

    def __init__(self):
        # ウィンドウ
        self.root: Optional[tk.Tk] = None

        # ファイルパス
        self.entry_var: Optional[tk.StringVar] = None
        # 変換メソッドの種類
        self.selected_method: Optional[tk.StringVar] = None

        # プログレスバー
        self.percent: Optional[tk.StringVar] = None
        self.pb: Optional[ttk.Progressbar] = None
        self.remain: Optional[tk.StringVar] = None


class WindowBuilder:
    """:class:`MyWindow` を組み立てる Builder。

    ``create_*`` メソッドはウィジェットを生成して返すと同時に、状態変数を
    :attr:`window` へ登録する。配置 (grid) は呼び出し側の責務とする。
    """

    def __init__(self):
        # ウィンドウ
        self.window = MyWindow()

    def create_window(self, geometry: str) -> None:
        """ルートウィンドウを生成する。

        ドラッグ&ドロップを利用するため、``tk.Tk`` ではなく
        ``TkinterDnD.Tk`` を使用する。

        :param geometry: ``"510x420"`` 形式のウィンドウサイズ。
        """
        # TkinterDnDを使用してドラッグアンドドロップをサポートするウィンドウを作成
        root = TkinterDnD.Tk()
        root.geometry(geometry)
        root.title("VideoConverter")
        self.window.root = root

    def create_browse_button(self) -> tk.Button:
        """ファイル選択ダイアログを開くボタンを生成する。

        :return: 「ファイルを選択」ボタン。
        """
        browse_button = tk.Button(
            self.window.root,
            text="ファイルを選択",
            command=lambda: _browse_file(self.window.entry_var),
        )
        return browse_button

    def create_path_entry(self, width: int) -> tk.Entry:
        """ファイルパス入力欄を生成する。

        入力欄自体をドロップ対象として登録する。

        :param width: 入力欄の幅 (文字数)。
        :return: ファイルパス入力欄。
        """
        self.window.entry_var = tk.StringVar()
        entry = tk.Entry(
            self.window.root, textvariable=self.window.entry_var, width=width
        )
        # エントリーウィジェットにドラッグアンドドロップを設定
        entry.drop_target_register(DND_FILES)
        entry.dnd_bind("<<Drop>>", lambda e: _drop_file(e, self.window.entry_var))
        return entry

    def create_convert_button(self, writer: "TkPBarWriter") -> tk.Button:
        """変換を開始するボタンを生成する。

        :param writer: 進捗をウィジェットへ反映するライター。
        :return: 「変換」ボタン。
        """
        button = tk.Button(
            self.window.root,
            text="変換",
            command=lambda: convert_and_send(self.window, writer),
        )
        return button

    def create_method_options(self) -> list[tk.Radiobutton]:
        """変換方式を選択するラジオボタン群を生成する。

        選択値は :data:`METHODS` のキー (``to_mp4``、``audio_extract``、
        ``audio_eliminate``、``compress``) に対応する。

        :return: ラジオボタンのリスト。
        """
        texts = ["MP4 へ変換", "MP3 へ変換", "音声除去", "動画圧縮"]
        methods = ["to_mp4", "audio_extract", "audio_eliminate", "compress"]

        # 選択された値を格納する変数を作成
        self.window.selected_method = tk.StringVar()
        self.window.selected_method.set("to_mp4")

        # ラジオボタンを作成
        radio_buttons = [
            tk.Radiobutton(
                self.window.root,
                variable=self.window.selected_method,
                text=text,
                value=method,
            )
            for text, method in zip(texts, methods)
        ]
        return radio_buttons

    def create_pbar_items(
        self, pbar_length: int
    ) -> tuple[tk.Label, ttk.Progressbar, tk.Label]:
        """進捗率ラベル・プログレスバー・残り時間ラベルを生成する。

        プログレスバーは進捗を 0.0〜1.0 の割合で受け取る。

        :param pbar_length: プログレスバーの長さ (ピクセル)。
        :return: (進捗率ラベル, プログレスバー, 残り時間ラベル) のタプル。
        """
        self.window.percent = tk.StringVar()
        self.window.percent.set("  0%")
        percent = tk.Label(self.window.root, textvariable=self.window.percent)

        self.window.pb = ttk.Progressbar(
            self.window.root, length=pbar_length, mode="determinate", maximum=1
        )

        self.window.remain = tk.StringVar()
        self.window.remain.set("[00:00<00:00] 0.0s/it")
        remain = tk.Label(self.window.root, textvariable=self.window.remain)

        return percent, self.window.pb, remain

    def create_console(self, height: int, width: int) -> tk.Text:
        """標準出力を表示するコンソールを生成する。

        副作用として ``sys.stdout`` を :class:`StdoutRedirector` へ差し替える。

        :param height: コンソールの高さ (行数)。
        :param width: コンソールの幅 (文字数)。
        :return: コンソールとして使うテキストウィジェット。
        """
        console = tk.Text(self.window.root, wrap=tk.WORD, height=height, width=width)

        stdout_redirector = StdoutRedirector(console)
        sys.stdout = stdout_redirector

        return console


class TkPBarWriter:
    """進捗の通知を受けて GUI のプログレスバーを更新するクラス (Observer)。

    :param total: 動画の合計時間 (秒)。生成時点では不明なため既定は ``None``
        で、変換開始時に :func:`convert_and_send` が :meth:`reset` を通じて
        設定する。
    """

    def __init__(self, total: Optional[float] = None):
        self.total = total
        self.start_time = time.time()

    def reset(self, total: float) -> None:
        """変換の開始に合わせて合計時間と計測開始時刻を初期化する。

        :param total: 動画の合計時間 (秒)。
        """
        self.total = total
        self.start_time = time.time()

    def callback(self, step: float, window: MyWindow) -> None:
        """進捗をウィジェットへ反映する。

        :param step: 変換済みの再生時間 (秒)。
        :param window: 更新対象のウィジェットを保持するウィンドウ。
        """
        window.pb.configure(value=step / self.total)
        window.pb.update()

        dt = time.time() - self.start_time
        mean_speed = dt / step if step > 0 else 0
        remain_time = mean_speed * (self.total - step) if step > 0 else 0

        dt = "{:02d}:{:02d}".format(*divmod(int(dt), 60))
        remain_time = "{:02d}:{:02d}".format(*divmod(int(remain_time), 60))

        # StringVarを使用して値を更新
        window.percent.set(f"{int(100 * step / self.total):02d}%")
        window.remain.set(f"[{dt}<{remain_time}] {mean_speed:.1f}s/it")


def create_window() -> MyWindow:
    """全ウィジェットを生成・配置したウィンドウを構築する。

    ``mainloop()`` は呼び出さないため、テストから利用できる。

    :return: 構築済みのウィンドウ。
    """
    builder = WindowBuilder()
    builder.create_window(geometry="510x420")

    # ウィンドウ全体にもドラッグアンドドロップを設定
    builder.window.root.drop_target_register(DND_FILES)
    builder.window.root.dnd_bind(
        "<<Drop>>", lambda e: _drop_file(e, builder.window.entry_var)
    )

    # ファイルパス選択
    browse_button = builder.create_browse_button()
    path_entry = builder.create_path_entry(width=55)

    # ファイル変換
    pbar_writer = TkPBarWriter()
    convert_button = builder.create_convert_button(pbar_writer)
    radio_buttons = builder.create_method_options()

    # プログレスバー
    percent, pb, remain = builder.create_pbar_items(pbar_length=200)

    # コンソール
    console = builder.create_console(height=15, width=65)

    # レイアウト配置
    browse_button.grid(row=0, column=0, padx=20, pady=20)
    path_entry.grid(row=0, column=1, columnspan=4, padx=0, pady=20)
    convert_button.grid(row=1, column=0, padx=20, pady=0)
    for idx, radio_button in enumerate(radio_buttons):
        radio_button.grid(row=1, column=idx + 1)
    percent.grid(row=2, column=0, padx=20, pady=20)
    pb.grid(row=2, column=1, columnspan=2, padx=0, pady=0)
    remain.grid(row=2, column=3, columnspan=2, padx=20, pady=20)
    console.grid(row=3, column=0, columnspan=5, padx=20, pady=20)

    window = builder.window
    return window


def convert_and_send(window: MyWindow, pbar_writer: TkPBarWriter) -> None:
    """GUI の入力内容にもとづき変換を実行する。

    FFmpeg の実行と進捗受信を gevent の greenlet で並行に動かし、
    両者の完了を待ち合わせる。

    :param window: 入力値と進捗ウィジェットを保持するウィンドウ。
    :param pbar_writer: 進捗をウィジェットへ反映するライター。
    """
    # GUI から情報取得
    path_str = window.entry_var.get()
    method_str = window.selected_method.get()
    print(f"Path: {path_str}")
    print(f"Method: {method_str}")

    # プログレスバー書き込み設定
    total = float(ffmpeg.probe(path_str)["format"]["duration"])
    pbar_writer.reset(total)
    sender = FFmpegTCPSender(
        lambda step: pbar_writer.callback(step, window),
        total,
    )
    greenlet_progress = gevent.spawn(sender.tcp_handler, progress.PORT)

    # FFmpeg 変換設定
    pipeline = METHODS[method_str](path_str)
    pipeline = pipeline.global_args("-progress", f"tcp://127.0.0.1:{progress.PORT}")
    greenlet_ffmpeg = gevent.spawn(lambda: pipeline.run())

    gevent.joinall([greenlet_progress, greenlet_ffmpeg])


def open_window() -> None:
    """ウィンドウを構築し、イベントループを開始する。"""
    window = create_window()
    window.root.mainloop()


if __name__ == "__main__":
    open_window()
