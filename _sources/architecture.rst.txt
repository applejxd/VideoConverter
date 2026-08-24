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
   │  paths.resolve_io_paths で入出力を確定        │
   └──────────────────────┬───────────────────────┘
                          ▼
   ┌──────────────────────────────────────────────┐
   │ progress.py                                  │
   │  run_pipeline_with_observer                  │
   │  pipeline.run() + TCP 経由の進捗受信          │
   └──────────────────────────────────────────────┘

入出力パスの解決
----------------

入力の存在確認、既定の出力先の決定、入力と出力が同一かの判定は
:func:`~video_converter.paths.resolve_io_paths` にまとめています。
このモジュールは ``gevent`` にも ``progress`` にも依存しないため、
パス解決のためだけに import しても副作用がありません。

出力先が入力と同じファイルを指す場合は ``ValueError`` で停止します。
``to_mp4`` に ``.mp4`` を渡して ``output_path`` を省略した場合などが
これにあたり、そのまま実行すると FFmpeg が同じファイルを読み書きして
入力を破壊するためです。

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

いずれの pipeline にも ``overwrite_output()`` を付けているため、出力先が
既に存在する場合は上書きします。これが無いと FFmpeg が
``Overwrite? [y/N]`` の確認で停止し、進捗用の TCP 接続をしないまま終了して
変換が破綻します。

進捗の取得方法
--------------

FFmpeg は ``-progress <URL>`` オプションを与えると、``key=value`` 形式の
進捗情報を指定先へ書き出します。本ライブラリはこれを TCP で受け取ります。

#. :class:`~video_converter.progress.FFmpegTCPSender` が
   ``bind(("127.0.0.1", 0))`` で OS に空きポートを割り当てさせ、
   :attr:`~video_converter.progress.FFmpegTCPSender.port` で番号を公開する。
   空きを探してから改めて ``bind`` すると、その間に別プロセスへ取られる
   余地があるため、先に ``bind`` してから番号を読み出す。
#. pipeline に ``-progress tcp://127.0.0.1:<port>`` を付与する。
#. :meth:`~video_converter.progress.FFmpegTCPSender.tcp_handler` が
   接続を受け付け、受信した行を ``key`` と ``value`` に分解する。
#. ``out_time_ms`` から変換済みの再生時間を算出し、進捗として通知する。
   ``progress=end`` を受け取った時点で合計時間へ丸める。

FFmpeg の実行と進捗の受信は同時に行う必要があるため、``gevent`` の
greenlet を 2 つ ``spawn`` して ``joinall`` で待ち合わせています。
``joinall`` は greenlet の例外を伝播しないため、待ち合わせ後に
``successful()`` を確認して例外を再送出します。あわせて FFmpeg 側の
greenlet に ``link_exception`` を張り、FFmpeg が接続前に失敗した場合は
進捗側の待ち受けを直ちに打ち切ります。接続を待つ ``accept()`` にも
タイムアウト (:data:`~video_converter.progress.DEFAULT_ACCEPT_TIMEOUT`)
を設けており、これらが無いと FFmpeg の失敗時にハングします。

``gevent`` の ``monkey.patch_all()`` は、他のモジュールが ``ssl`` や
``socket`` を import するより先に適用する必要があるため、ライブラリ側では
なく :mod:`video_converter.__main__` の先頭で呼んでいます。

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
