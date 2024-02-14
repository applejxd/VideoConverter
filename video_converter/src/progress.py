import socket
import sys

import ffmpeg
import gevent
import psutil
import tqdm
from gevent import monkey

# monkey.patch_all()


def get_available_port(start=49152):
    # "LISTEN" 状態のポート番号をリスト化
    used_ports = [
        conn.laddr.port for conn in psutil.net_connections() if conn.status == "LISTEN"
    ]
    for port in range(start, 65535 + 1):
        # 未使用のポート番号ならreturn
        if port not in set(used_ports):
            return port
    raise RuntimeError("使用可能なポート番号がありません")


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
        if key == "out_time_ms":
            if value == "N/A":
                return
            time = round(float(value) / 1000000.0, 2)
            self.update_callback(time)
        elif key == "progress" and value == "end":
            self.update_callback(self.total)

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


def run_with_tcp_pbar(path, pipeline):
    pipeline = pipeline.global_args("-progress", f"tcp://127.0.0.1:{PORT}")

    total = float(ffmpeg.probe(path)["format"]["duration"])
    with tqdm.tqdm(total=total) as pbar:

        def pbar_callback(n):
            pbar.update(n - pbar_callback.n_pre)
            pbar_callback.n_pre = n

        pbar_callback.n_pre = 0
        sender = FFmpegTCPSender(total, pbar_callback)

        greenlet_progress = gevent.spawn(sender.tcp_handler)
        greenlet_ffmpeg = gevent.spawn(pipeline.run)
        gevent.joinall([greenlet_progress, greenlet_ffmpeg])
