import socket

from gevent import monkey

monkey.patch_all()

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
