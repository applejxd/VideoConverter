"""pytest の共通設定。

``video_converter.progress`` は gevent の monkey patch を前提とする。
テストは :mod:`video_converter.__main__` を経由しないため、
他のモジュールが ``ssl`` や ``socket`` を import するより先に、
ここで patch を適用する。
"""

from gevent import monkey

monkey.patch_all()
