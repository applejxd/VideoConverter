import socket
from typing import Optional

import ffmpeg
import gevent
import psutil
import tqdm
from gevent import monkey

monkey.patch_all()


def get_available_port(start: int = 49152) -> int:
    """
    使用可能なポート番号を取得する。

    :param start: 検索を開始するポート番号 (デフォルト: 49152)。
    :return: 使用可能なポート番号。
    :raises RuntimeError: 使用可能なポート番号がない場合。
    """
    # "LISTEN" 状態のポート番号をリスト化
    used_ports = {
        conn.laddr.port for conn in psutil.net_connections() if conn.status == "LISTEN"
    }
    for port in range(start, 65535 + 1):
        # 未使用のポート番号ならreturn
        if port not in used_ports:
            return port
    raise RuntimeError("使用可能なポート番号がありません")


PORT = get_available_port()


# Model (Observer pattern)
class FFmpegTCPSender:
    def __init__(self, pbar: tqdm.tqdm, total: float):
        """
        FFmpeg の TCP 送信者。

        :param pbar: tqdm プログレスバー。
        :param total: 動画の合計時間 (秒)。
        """
        # Observer pattern
        self.pbar = pbar
        self.total = total
        self.time_pre = 0
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection: Optional[socket.socket] = None

    def __del__(self):
        self.sock.close()

    def _connect(self, port):
        """
        TCP 接続を確立する。

        :param port: ポート番号。
        :return: socket.socket オブジェクト。
        """
        self.sock.bind(("127.0.0.1", port))
        self.sock.listen(1)
        self.connection, _ = self.sock.accept()
        return self.connection

    def _notify_pbar(self, key: str, value: str) -> None:
        """
        プログレスバーを更新する。

        :param key: FFmpeg から送信されたキー。
        :param value: FFmpeg から送信された値。
        """
        if key == "out_time_ms":
            if value == "N/A":
                return
            time = round(float(value) / 1000000.0, 2)
        elif key == "progress" and value == "end":
            time = self.total
        else:
            return

        self.pbar.update(time - self.time_pre)
        self.time_pre = time

    def tcp_handler(self, port: int) -> None:
        """
        TCP データの受信および処理を行う。

        :param port: ポート番号。
        """
        connection = self._connect(port)
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

                self._notify_pbar(key, value)
            data = lines[-1]


def run_with_tcp_pbar(path, pipeline):
    """
    FFmpeg の実行時に TCP 通信でプログレスバーを表示する。

    :param path: 動画のファイルパス。
    :param pipeline: FFmpeg の pipeline オブジェクト。
    :return: pipeline.run() の結果。
    """
    global PORT

    # TODO：AF_INET の TCP 通信以外にしたい
    pipeline = pipeline.global_args("-progress", f"tcp://127.0.0.1:{PORT}")

    total = float(ffmpeg.probe(path)["format"]["duration"])
    with tqdm.tqdm(total=total) as pbar:
        sender = FFmpegTCPSender(pbar, total)

        greenlet_progress = gevent.spawn(sender.tcp_handler, PORT)
        greenlet_ffmpeg = gevent.spawn(pipeline.run)
        gevent.joinall([greenlet_progress, greenlet_ffmpeg])
        
        # Return the result of pipeline.run()
        return greenlet_ffmpeg.value
