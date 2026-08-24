アーキテクチャ
==============

全体像
------

このライブラリは「変換処理の定義」と「実行・進捗表示」を分離しています。

.. code-block:: text

   ┌──────────────┐        ┌───────────────────────┐
   │ CLI (Fire)   │        │ GUI (Tkinter)         │
   │ __main__.py  │        │ gui.py                │
   └──────┬───────┘        └───────────┬───────────┘
          │ cli_wrapper                │ convert_and_send
          ▼                            ▼
   ┌──────────────────────────────────────────────┐
   │ compressor / converter / extractor           │
   │  → ffmpeg.nodes.Node (pipeline) を返すだけ    │
   └──────────────────────┬───────────────────────┘
                          ▼
   ┌──────────────────────────────────────────────┐
   │ progress.py                                  │
   │  pipeline.run() + TCP 経由の進捗受信          │
   └──────────────────────────────────────────────┘

pipeline を返す設計
-------------------

:func:`~video_converter.compressor.compress`、
:func:`~video_converter.converter.to_mp4`、
:func:`~video_converter.extractor.audio_extract`、
:func:`~video_converter.extractor.audio_eliminate` は、いずれも FFmpeg を
その場で実行せず、``ffmpeg.nodes.Node`` (pipeline) を組み立てて返します。

こうすることで、呼び出し側が実行前に ``global_args()`` で
``-progress tcp://...`` を追加できます。変換の定義と実行タイミングを
分離しているため、CLI と GUI で同じ変換関数を再利用できます。

進捗の取得方法
--------------

FFmpeg は ``-progress <URL>`` オプションを与えると、``key=value`` 形式の
進捗情報を指定先へ書き出します。本ライブラリはこれを TCP で受け取ります。

#. :func:`~video_converter.progress.get_available_port` が ``psutil`` で
   ``LISTEN`` 状態のポートを調べ、未使用のポート (既定は 49152 以降) を選ぶ。
#. pipeline に ``-progress tcp://127.0.0.1:<port>`` を付与する。
#. :meth:`~video_converter.progress.FFmpegTCPSender.tcp_handler` が
   そのポートで待ち受け、受信した行を ``key`` と ``value`` に分解する。
#. ``out_time_ms`` から変換済みの再生時間を算出し、進捗として通知する。
   ``progress=end`` を受け取った時点で合計時間へ丸める。

FFmpeg の実行と進捗の受信は同時に行う必要があるため、``gevent`` の
greenlet を 2 つ ``spawn`` して ``joinall`` で待ち合わせています。
``progress.py`` の冒頭で ``monkey.patch_all()`` を呼び、標準ライブラリの
ソケットを協調的にしています。

Observer パターン
-----------------

:class:`~video_converter.progress.FFmpegTCPSender` が Subject、進捗の表示側が
Observer にあたります。Observer は 2 種類あり、
:meth:`~video_converter.progress.FFmpegTCPSender._notify_pbar` が
``n`` 属性の有無で実行時に判別します。

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - 利用側
     - Observer
     - 通知方法
   * - CLI
     - ``tqdm.tqdm``
     - ``pbar.update(差分秒数)``
   * - GUI
     - :class:`~video_converter.gui.TkPBarWriter` のコールバック
     - ``pbar(累積秒数)`` を呼び出す

この分岐により、``progress.py`` は tqdm にも Tkinter にも依存せずに
両方の表示先へ対応できます。

Builder パターン (GUI)
----------------------

GUI では、ウィジェットの生成と配置を分離しています。

- :class:`~video_converter.gui.MyWindow` -- ウィジェットと状態変数
  (``tk.StringVar`` など) への参照だけを保持するコンテナ。
- :class:`~video_converter.gui.WindowBuilder` -- ``create_*`` メソッドで
  ウィジェットを生成し、状態変数を ``MyWindow`` へ登録する。
- :func:`~video_converter.gui.create_window` -- Builder を呼び出したうえで
  ``grid()`` によるレイアウトを行い、完成した ``MyWindow`` を返す。

``create_window()`` は ``mainloop()`` を呼ばないため、テストから
ウィンドウ生成のみを検証できます (``tests/test_gui.py``)。
実際にイベントループを開始するのは
:func:`~video_converter.gui.open_window` です。

なお :meth:`~video_converter.gui.WindowBuilder.create_console` は副作用として
``sys.stdout`` を :class:`~video_converter.gui.StdoutRedirector` へ差し替え、
標準出力をウィンドウ内のテキストウィジェットへ転送します。

CLI のデコレータ
----------------

CLI 側では :func:`~video_converter.utils.cli_wrapper` が変換関数を包み、
返された pipeline を :func:`~video_converter.progress.run_with_tcp_pbar` へ
渡します。``__main__.py`` では Fire へ登録する時点でこのデコレータを適用して
おり、変換関数自体には進捗表示の知識を持たせていません。
