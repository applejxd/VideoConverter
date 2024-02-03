import sys
import time
import tkinter as tk
from tkinter import filedialog, ttk

import ffmpeg
import gevent

from video_converter.src import progress
from video_converter.src.compressor import compress
from video_converter.src.conveter import to_mp4
from video_converter.src.extractor import audio_eliminate, audio_extract
from video_converter.src.progress import FFmpegTCPSender


def _create_window():
    window = tk.Tk()
    window.geometry("510x420")
    window.title("VideoConverter")
    return window


def _browse_file(string_var):
    file_path = filedialog.askopenfilename()
    string_var.set(file_path)


class StdoutRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)  # テキストを最後にスクロール


class TkPBarWriter:
    def __init__(self, total):
        self.total = total
        self.start_time = time.time()

    def callback(self, step, pb, percent_label, remain_label):
        pb.configure(value=step / self.total)
        pb.update()

        dt = time.time() - self.start_time
        mean_speed = dt / step
        remain_time = mean_speed * self.total - dt

        dt = "{:02d}:{:02d}".format(*divmod(int(dt), 60))
        remain_time = "{:02d}:{:02d}".format(*divmod(int(remain_time), 60))
        percent_label["text"] = f"{int(100*step/self.total):02d}%"
        remain_label["text"] = f"[{dt}<{remain_time}] {mean_speed:.1f}s/it"


class Window:
    def __init__(self):
        self.root = _create_window()

        # ファイル選択ボタン
        self._create_select_button()
        # ファイルパス表示
        self.entry_var = self._create_path_entry()
        # 変換ボタン
        self._create_convert_button()
        self.selected_method = self._create_method_options()

        self.percent = tk.Label(self.root, text="  0%")
        self.percent.grid(row=2, column=0, padx=20, pady=20)
        self.pb = ttk.Progressbar(self.root, length=200, mode="determinate", maximum=1)
        self.pb.grid(row=2, column=1, columnspan=2, padx=0, pady=0)
        self.remain = tk.Label(self.root, text=f"[00:00<00:00], 0s/it")
        self.remain.grid(row=2, column=3, columnspan=2, padx=20, pady=20)

        # コンソール
        self._create_console()

        self.root.mainloop()

    def _create_select_button(self):
        browse_button = tk.Button(
            self.root,
            text="ファイルを選択",
            command=lambda: _browse_file(self.entry_var),
        )
        browse_button.grid(row=0, column=0, padx=20, pady=20)
        return browse_button

    def _create_path_entry(self):
        entry_var = tk.StringVar()
        entry = tk.Entry(self.root, textvariable=entry_var, width=55)
        entry.grid(row=0, column=1, columnspan=4, padx=0, pady=20)
        return entry_var

    def _convert(self):
        path_str = self.entry_var.get()
        method_str = self.selected_method.get()
        print(f"Path: {path_str}")
        print(f"Method: {method_str}")

        # プログレスバー書き込み
        total = float(ffmpeg.probe(path_str)["format"]["duration"])
        pbar_writer = TkPBarWriter(total)
        sender = FFmpegTCPSender(
            total,
            lambda step: pbar_writer.callback(step, self.pb, self.percent, self.remain),
        )
        greenlet_progress = gevent.spawn(sender.tcp_handler)

        # FFmpeg 変換
        pipeline = globals()[method_str](path_str)
        pipeline = pipeline.global_args("-progress", f"tcp://127.0.0.1:{progress.PORT}")
        greenlet_ffmpeg = gevent.spawn(lambda: pipeline.run())

        gevent.joinall([greenlet_progress, greenlet_ffmpeg])

    def _create_convert_button(self):
        button = tk.Button(self.root, text="変換", command=self._convert)
        button.grid(row=1, column=0, padx=20, pady=0)

    def _create_method_options(self):
        texts = ["MP4 へ変換", "MP3 へ変換", "音声除去", "動画圧縮"]
        methods = ["to_mp4", "audio_extract", "audio_eliminate", "compress"]

        # 選択された値を格納する変数を作成
        selected_method = tk.StringVar()
        selected_method.set("to_mp4")

        # ラジオボタンを作成して配置
        for idx, (text, method) in enumerate(zip(texts, methods)):
            radio_button = tk.Radiobutton(
                self.root, text=text, variable=selected_method, value=method
            )
            radio_button.grid(row=1, column=idx + 1)

        return selected_method

    def _create_console(self):
        output_text = tk.Text(self.root, wrap=tk.WORD, height=15, width=65)
        output_text.grid(row=3, column=0, columnspan=5, padx=20, pady=20)
        stdout_redirector = StdoutRedirector(output_text)
        sys.stdout = stdout_redirector


def open_window():
    Window()


if __name__ == "__main__":
    open_window()
