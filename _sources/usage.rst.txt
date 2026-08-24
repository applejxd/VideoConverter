使い方
======

事前準備
--------

FFmpeg 本体が必要です。``ffmpeg-python`` は FFmpeg のラッパーであり、
FFmpeg 実行ファイルを同梱していないため、別途インストールして ``PATH`` を
通してください。

.. code-block:: powershell

   # Windows 11
   winget install astral-sh.uv Gyan.FFmpeg

   # 依存関係のインストール
   uv sync

CLI
---

``python -m video_converter <サブコマンド>`` の形式で実行します。
インストール後は ``video-converter <サブコマンド>`` でも起動できます。
引数の解析には Fire を利用しているため、``--help`` で各コマンドの
引数を確認できます。

.. code-block:: powershell

   python -m video_converter --help

出力先 (``output_path``) はいずれのコマンドでも省略可能です。省略した場合は
入力ファイルと同じディレクトリに、下表の規則で命名されたファイルが作られます。

.. list-table::
   :header-rows: 1
   :widths: 20 30 25 25

   * - サブコマンド
     - 処理
     - 主な引数
     - 既定の出力名
   * - ``compress``
     - 動画を再エンコードして圧縮
     - ``input_path``, ``output_path``, ``crf``
     - ``<元の名前>_compressed.mp4``
   * - ``to_mp4``
     - ``.mp4`` へ変換
     - ``input_path``, ``output_path``
     - ``<元の名前>.mp4``
   * - ``audio_extract``
     - 音声を ``.mp3`` で抽出
     - ``input_path``, ``output_path``
     - ``<元の名前>.mp3``
   * - ``audio_eliminate``
     - 音声トラックを除去
     - ``input_path``, ``output_path``
     - ``<元の名前>_wo_audio.mp4``
   * - ``gui``
     - GUI を起動
     - なし
     - --

実行例:

.. code-block:: powershell

   # 動画を圧縮する (crf は小さいほど高品質・大容量。既定値は 23)
   python -m video_converter compress input.mp4 --crf 23

   # .mov を .mp4 へ変換する
   python -m video_converter to_mp4 input.mov

   # 出力先を明示する
   python -m video_converter audio_extract input.mp4 --output_path C:\tmp\sound.mp3

   # 音声トラックを取り除く
   python -m video_converter audio_eliminate input.mp4

入力ファイルが存在しない場合は ``FileNotFoundError`` が送出されます。
変換中は tqdm による進捗バーが表示されます。

.. note::

   出力先のファイルが既に存在する場合は、確認せずに上書きします。

.. note::

   出力先が入力と同じファイルを指す場合は ``ValueError`` で停止します。
   ``to_mp4 input.mp4`` のように入力と同じ拡張子で ``output_path`` を
   省略した場合が該当します。別の出力先を明示してください。

FFmpeg が異常終了した場合は ``ffmpeg.Error`` が、進捗用の TCP 接続が
制限時間内に行われなかった場合は ``TimeoutError`` が送出されます。

GUI
---

.. code-block:: powershell

   python -m video_converter gui

ウィンドウの操作手順は次のとおりです。

#. **ファイルを指定する。**\ 「ファイルを選択」ボタンからダイアログを開くか、
   動画ファイルをウィンドウ (または入力欄) へ直接ドラッグ&ドロップします。
#. **変換方式を選ぶ。** ラジオボタンから「MP4 へ変換」「MP3 へ変換」
   「音声除去」「動画圧縮」のいずれかを選択します。既定は「MP4 へ変換」です。
#. **「変換」ボタンを押す。** 進捗率・プログレスバー・残り時間が更新されます。
   :func:`~video_converter.gui.convert_and_send` が出力する変換対象パスと
   変換方式は、ウィンドウ下部のコンソール領域へ表示されます。

実行ファイルの作成
------------------

PyInstaller で単一実行ファイルにまとめられます。PyInstaller は任意の依存
(``build`` extra) のため、先にインストールしてください。

.. code-block:: powershell

   uv sync --extra build
   uv run pyinstaller .\src\video_converter\gui.py --onefile --noconsole
