# VideoConverter プロジェクト概要

## プロジェクトの目的

VideoConverter は、FFmpeg を使用して動画ファイルを変換・圧縮・編集するための Python ライブラリです。コマンドラインインターフェース（CLI）と グラフィカルユーザーインターフェース（GUI）の両方を提供し、ユーザーが簡単に動画ファイルを操作できるようにします。

## 主な機能

- 動画ファイルの MP4 形式への変換
- 動画ファイルの圧縮
- 動画から音声の抽出（MP3 形式）
- 動画から音声の削除
- 進捗状況の表示（CLI とGUI の両方で）

## 技術スタック

- Python 3.11
- FFmpeg（外部依存）
- ffmpeg-python（Python バインディング）
- Fire（CLI インターフェース）
- Tkinter（GUI インターフェース）
- gevent（非同期処理）
- tqdm（CLI プログレスバー）

## 使用方法

### CLI

```bash
# 動画圧縮
python -m video_converter compress <動画ファイルパス>

# MP4 形式への変換
python -m video_converter to_mp4 <動画ファイルパス>

# 音声抽出
python -m video_converter audio_extract <動画ファイルパス>

# 音声削除
python -m video_converter audio_eliminate <動画ファイルパス>

# GUI 起動
python -m video_converter gui
```

### GUI

GUI では、以下の操作が可能です：

1. ファイル選択ボタンで動画ファイルを選択
2. 変換方法（MP4 変換、MP3 抽出、音声削除、動画圧縮）を選択
3. 変換ボタンをクリックして処理を開始
4. プログレスバーで進捗状況を確認
