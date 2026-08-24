video-converter documentation
=============================

``video_converter`` は `ffmpeg-python <https://github.com/kkroening/ffmpeg-python>`_ を
用いた動画変換ライブラリです。CLI (`Fire <https://github.com/google/python-fire>`_) と
GUI (Tkinter) の 2 つのインターフェースから、以下の処理を行えます。

- 動画の圧縮 (CRF 指定)
- ``.mp4`` への形式変換
- 音声の ``.mp3`` 抽出
- 音声トラックの除去

いずれの処理でも、FFmpeg の ``-progress`` オプションを利用した進捗表示に
対応しています (CLI では tqdm、GUI ではプログレスバーウィジェット)。

.. toctree::
   :maxdepth: 2
   :caption: 目次

   readme
   usage
   architecture
   api/modules

索引
----

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
