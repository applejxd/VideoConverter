import argparse
import socket
import sys
import threading

import ffmpeg
import gevent
from gevent import monkey

monkey.patch_all()

from tqdm import tqdm

PORT = 50057


class FFmpegTCPSender:
    def __init__(self, total, update_callback):
        self.total = total
        self.update_callback = update_callback
        self.n = 0

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        self.sock.close()

    def _connect(self, port):
        self.sock.bind(("127.0.0.1", port))
        self.sock.listen(1)
        connection, client_address = self.sock.accept()
        return connection

    def _update_pbar(self, key, value):
        dt = 0
        if key == "out_time_ms":
            if value == "N/A":
                return
            time = round(float(value) / 1000000.0, 2)
            dt = time - self.n
        elif key == "progress" and value == "end":
            dt = self.total - self.n

        self.update_callback(dt)
        self.n = self.n + dt

    def tcp_handler(self):
        connection = self._connect(PORT)
        data = b""
        while True:
            more_data = connection.recv(16)
            if not more_data:
                break

            data += more_data
            lines = data.split(b"\n")

            for line in lines[:-1]:
                line = line.decode()
                parts = line.split("=")

                key = parts[0] if len(parts) > 0 else None
                value = parts[1] if len(parts) > 1 else None

                self._update_pbar(key, value)
            data = lines[-1]


def cli_pbar(file_path):
    total = float(ffmpeg.probe(file_path)["format"]["duration"])
    with tqdm(total=total) as pbar:
        callback = lambda x: pbar.update(x)
        FFmpegTCPSender(total, callback).tcp_handler()


def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_filename", help="Input filename")
    parser.add_argument("out_filename", help="Output filename")
    args = parser.parse_args()

    total = float(ffmpeg.probe(args.in_filename)["format"]["duration"])
    with tqdm(total=total) as pbar:
        callback = lambda x: pbar.update(x)
        sender = FFmpegTCPSender(total, callback)

        # gevent.spawnを使用して非同期タスクを開始
        greenlet = gevent.spawn(sender.tcp_handler)

        sepia_values = [
            0.393,
            0.769,
            0.189,
            0,
            0.349,
            0.686,
            0.168,
            0,
            0.272,
            0.534,
            0.131,
        ]
        try:
            (
                ffmpeg.input(args.in_filename)
                .colorchannelmixer(*sepia_values)
                .output(args.out_filename)
                .global_args("-progress", f"tcp://127.0.0.1:{PORT}")
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            print(e.stderr, file=sys.stderr)
            sys.exit(1)

        # gevent.joinallで全てのタスクが完了するまで待つ
        gevent.joinall([greenlet])


if __name__ == "__main__":
    _main()
