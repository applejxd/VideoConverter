import sys
import time
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional

import ffmpeg
import gevent

from video_converter.src import progress
from video_converter.src.compressor import compress
from video_converter.src.conveter import to_mp4
from video_converter.src.extractor import audio_eliminate, audio_extract
from video_converter.src.progress import FFmpegTCPSender


def _browse_file(string_var):
    file_path = filedialog.askopenfilename()
    string_var.set(file_path)


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        # テキストを最後にスクロール
        self.text_widget.see(tk.END)


class MyWindow:
    def __init__(self):
        # ウィンドウ
        self.root = None

        # ファイルパス
        self.entry_var = None
        # 変換メソッドの種類
        self.selected_method = None

        # プログレスバー
        self.percent = None
        self.pb = None
        self.remain = None


class WindowBuilder:
    def __init__(self):
        # ウィンドウ
        self.window = MyWindow()

    def create_window(self, geometry: str) -> None:
        root = tk.Tk()
        root.geometry(geometry)
        root.title("VideoConverter")
        self.window.root = root

    def create_browse_button(self):
        browse_button = tk.Button(
            self.window.root,
            text="ファイルを選択",
            command=lambda: _browse_file(self.window.entry_var),
        )
        return browse_button

    def create_path_entry(self, width):
        self.window.entry_var = tk.StringVar()
        entry = tk.Entry(
            self.window.root, textvariable=self.window.entry_var, width=width
        )
        return entry

    def create_convert_button(self, writer):
        button = tk.Button(
            self.window.root,
            text="変換",
            command=lambda: convert_and_send(self.window, writer),
        )
        return button

    def create_method_options(self):
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

    def create_pbar_items(self, pbar_length):
        self.window.percent = tk.StringVar()
        self.window.percent.set("  0%")
        percent = tk.Label(self.window.root, textvariable=self.window.percent)

        self.window.pb = ttk.Progressbar(
            self.window.root, length=pbar_length, mode="determinate", maximum=1
        )

        self.window.remain = tk.StringVar()
        self.window.remain = f"[00:00<00:00], 0s/it"
        remain = tk.Label(self.window.root, textvariable=self.window.remain)

        return percent, self.window.pb, remain

    def create_console(self, height, width):
        console = tk.Text(self.window.root, wrap=tk.WORD, height=height, width=width)

        stdout_redirector = StdoutRedirector(console)
        sys.stdout = stdout_redirector

        return console


class TkPBarWriter:
    def __init__(self, total: Optional[float] = None):
        self.total = total
        self.start_time = time.time()

    def callback(self, step: float, window: MyWindow):
        window.pb.configure(value=step / self.total)
        window.pb.update()

        dt = time.time() - self.start_time
        mean_speed = dt / step
        remain_time = mean_speed * self.total - dt

        dt = "{:02d}:{:02d}".format(*divmod(int(dt), 60))
        remain_time = "{:02d}:{:02d}".format(*divmod(int(remain_time), 60))
        window.percent_label["text"] = f"{int(100*step/self.total):02d}%"
        window.remain_label["text"] = f"[{dt}<{remain_time}] {mean_speed:.1f}s/it"


def create_window() -> MyWindow:
    builder = WindowBuilder()
    builder.create_window(geometry="510x420")

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
    # GUI から情報取得
    path_str = window.entry_var.get()
    method_str = window.selected_method.get()
    print(f"Path: {path_str}")
    print(f"Method: {method_str}")

    # プログレスバー書き込み設定
    total = float(ffmpeg.probe(path_str)["format"]["duration"])
    pbar_writer.total = total
    sender = FFmpegTCPSender(
        total,
        lambda step: pbar_writer.callback(step, window),
    )
    greenlet_progress = gevent.spawn(sender.tcp_handler)

    # FFmpeg 変換設定
    pipeline = globals()[method_str](path_str)
    pipeline = pipeline.global_args("-progress", f"tcp://127.0.0.1:{progress.PORT}")
    greenlet_ffmpeg = gevent.spawn(lambda: pipeline.run())

    gevent.joinall([greenlet_progress, greenlet_ffmpeg])


def open_window():
    window = create_window()
    window.root.mainloop()


if __name__ == "__main__":
    open_window()
