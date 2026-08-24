"""FFmpeg の進捗を TCP 経由で受け取り、プログレスバーへ反映するモジュール。

FFmpeg の ``-progress tcp://127.0.0.1:<port>`` オプションを利用し、変換の
進捗を別プロセスから受信する。受信側は Observer パターンで実装されており、
:class:`FFmpegTCPSender` (Subject) が tqdm プログレスバーまたは GUI の
コールバック関数 (Observer) へ進捗を通知する。
"""

import os
import socket
from typing import Callable, Optional, Union

import ffmpeg
import gevent
import tqdm
from gevent import monkey

monkey.patch_all()

#: FFmpeg からの進捗用 TCP 接続を待つ既定の秒数。
#: FFmpeg が接続前に終了した場合に待ち続けないための上限。
DEFAULT_ACCEPT_TIMEOUT = 30.0

# tqdm の監視スレッドは gevent が patch した threading と噛み合わず、
# インタプリタ終了時に LoopExit を送出するため無効化する
tqdm.tqdm.monitor_interval = 0


# Model (Observer pattern)
class FFmpegTCPSender:
    def __init__(
        self,
        pbar: Union[tqdm.tqdm, Callable[[float], None]],
        total: float,
        timeout: float = DEFAULT_ACCEPT_TIMEOUT,
    ):
        """
        FFmpeg の進捗を TCP で受信し、プログレスバーへ通知する Subject。

        :param pbar: 進捗の通知先 (Observer)。``n`` 属性を持つ tqdm プログレス
            バー、または経過秒数を 1 引数で受け取るコールバック関数のいずれか。
            どちらであるかは :meth:`_notify_pbar` が実行時に判別する。
        :param total: 動画の合計時間 (秒)。
        :param timeout: FFmpeg からの接続を待つ秒数。FFmpeg が接続前に
            終了した場合に待ち続けないための上限。
        """
        # Observer pattern
        self.pbar = pbar
        self.total = total
        self.time_pre = 0
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # ポート番号 0 を指定して OS に空きポートを割り当てさせる。
        # 事前に空きを探して後から bind すると、その間に別プロセスへ
        # 取られる余地がある
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.connection: Optional[socket.socket] = None

    @property
    def port(self) -> int:
        """待ち受けているポート番号。

        :return: OS が割り当てたポート番号。
        """
        return self.sock.getsockname()[1]

    def close(self) -> None:
        """待ち受けソケットと接続済みソケットを閉じる。"""
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        self.sock.close()

    def __del__(self) -> None:
        """デストラクタ。ソケットを閉じる。"""
        self.close()

    def _connect(self) -> socket.socket:
        """
        FFmpeg からの TCP 接続を受け付ける。

        :return: 接続済みの socket.socket オブジェクト。
        :raises TimeoutError: ``timeout`` 秒以内に FFmpeg が接続してこない場合。
            FFmpeg が起動直後に終了したときに待ち続けないためのガード。
        """
        self.sock.settimeout(self.timeout)
        try:
            self.connection, _ = self.sock.accept()
        except socket.timeout as exc:
            raise TimeoutError(
                f"FFmpeg が {self.timeout} 秒以内に "
                f"127.0.0.1:{self.port} へ接続しませんでした"
            ) from exc
        return self.connection
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

        update_value = time - self.time_pre
        # tqdmの場合はn属性を使用、それ以外の場合（GUI用のコールバック関数）は直接更新
        if hasattr(self.pbar, "n"):
            if 0 <= update_value <= self.total - self.pbar.n:
                self.pbar.update(update_value)
                self.time_pre = time
        else:
            # GUI用のコールバック関数の場合
            if 0 <= update_value <= self.total:
                self.pbar(time)  # コールバック関数を呼び出し
                self.time_pre = time

    def tcp_handler(self) -> None:
        """
        TCP データの受信および処理を行う。

        :raises TimeoutError: FFmpeg が制限時間内に接続してこない場合。
        """
        try:
            connection = self._connect()
            data = b""
            while True:
                more_data = connection.recv(4096)
                if not more_data:
                    break

                data += more_data
                lines = data.split(b"\n")

                for line in lines[:-1]:
                    key, _, value = line.decode().partition("=")
                    self._notify_pbar(key, value)
                data = lines[-1]
        finally:
            self.close()


def probe_duration(path: Union[str, os.PathLike]) -> float:
    """動画の合計再生時間を取得する。

    :param path: 動画のファイルパス。
    :return: 合計再生時間 (秒)。
    """
    return float(ffmpeg.probe(path)["format"]["duration"])


def run_pipeline_with_observer(
    pipeline: ffmpeg.nodes.Node,
    observer: Union[tqdm.tqdm, Callable[[float], None]],
    total: float,
    timeout: float = DEFAULT_ACCEPT_TIMEOUT,
) -> tuple[Optional[bytes], Optional[bytes]]:
    """FFmpeg を実行し、進捗を Observer へ通知する。

    :param pipeline: FFmpeg の pipeline オブジェクト。
    :param observer: 進捗の通知先。tqdm プログレスバーまたはコールバック関数。
    :param total: 動画の合計時間 (秒)。
    :param timeout: FFmpeg からの接続を待つ秒数。
    :return: ``pipeline.run()`` の戻り値 (stdout, stderr) のタプル。
        ``capture_stdout`` / ``capture_stderr`` を指定していないため、
        いずれの要素も ``None`` になる。
    :raises ffmpeg.Error: FFmpeg が異常終了した場合。
    :raises TimeoutError: FFmpeg が制限時間内に進捗用の TCP 接続を
        行わなかった場合。
    """
    # 先に bind してから FFmpeg へポート番号を伝えるため、
    # 取得したポートを他プロセスに奪われる余地がない
    sender = FFmpegTCPSender(observer, total, timeout)
    # TODO：AF_INET の TCP 通信以外にしたい
    pipeline = pipeline.global_args("-progress", f"tcp://127.0.0.1:{sender.port}")

    greenlet_progress = gevent.spawn(sender.tcp_handler)
    greenlet_ffmpeg = gevent.spawn(pipeline.run)
    # FFmpeg が接続前に失敗した場合、進捗側の待ち受けを直ちに打ち切る
    greenlet_ffmpeg.link_exception(lambda _: greenlet_progress.kill(block=False))
    gevent.joinall([greenlet_progress, greenlet_ffmpeg])

    # gevent.joinall は greenlet の例外を送出しないため、明示的に確認する
    if not greenlet_ffmpeg.successful():
        greenlet_ffmpeg.get()
    if not greenlet_progress.successful():
        greenlet_progress.get()

    # Return the result of pipeline.run()
    return greenlet_ffmpeg.value


def run_with_tcp_pbar(
    path: Union[str, os.PathLike], pipeline: ffmpeg.nodes.Node
) -> tuple[Optional[bytes], Optional[bytes]]:
    """
    FFmpeg の実行時に TCP 通信でプログレスバーを表示する。

    :param path: 動画のファイルパス。合計時間の取得に使用する。
    :param pipeline: FFmpeg の pipeline オブジェクト。
    :return: ``pipeline.run()`` の戻り値 (stdout, stderr) のタプル。
        ``capture_stdout`` / ``capture_stderr`` を指定していないため、
        いずれの要素も ``None`` になる。
    :raises ffmpeg.Error: FFmpeg が異常終了した場合。
    :raises TimeoutError: FFmpeg が制限時間内に進捗用の TCP 接続を
        行わなかった場合。
    """
    total = probe_duration(path)
    with tqdm.tqdm(total=total) as pbar:
        return run_pipeline_with_observer(pipeline, pbar, total)
