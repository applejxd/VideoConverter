# VideoConverter 進捗状況

## 完了した機能

- [x] 基本的な CLI インターフェース（Fire を使用）
- [x] 基本的な GUI インターフェース（Tkinter を使用）
- [x] 動画圧縮機能
- [x] MP4 形式への変換機能
- [x] 音声抽出機能
- [x] 音声削除機能
- [x] CLI での進捗表示（tqdm を使用）
- [x] GUI での進捗表示（Tkinter プログレスバーを使用）
- [x] FFmpeg との連携（ffmpeg-python を使用）
- [x] 非同期処理（gevent を使用）
- [x] 基本的なテスト（Python-Fireに登録されている機能のテスト）

## 現在の状態

### 2025/3/9 - テストの追加と `audio_eliminate` 関数のバグ修正

以下の変更を行いました：

1. `tests/test_cli_commands.py` を作成し、以下の機能のテストを実装
   - `compress` - 動画圧縮機能
   - `to_mp4` - MP4形式への変換機能
   - `audio_extract` - 音声抽出機能
   - `audio_eliminate` - 音声削除機能

2. `tests/test_gui.py` を作成し、GUIが正常に作成されるかテスト

3. `tests/run_tests.py` を作成し、すべてのテストを一括実行できるように

4. `extractor.py` の `audio_eliminate` 関数のバグを修正
   ```python
   # 修正前
   pipeline = ffmpeg.input(str(input_path)).output(str(output_path)).global_args("-an")
   
   # 修正後
   pipeline = ffmpeg.input(str(input_path)).output(str(output_path), **{'an': None})
   ```
   
   FFmpegの `-an` オプション（音声を削除するオプション）の指定方法が正しくなかったため、ffmpeg-pythonの正しい指定方法に修正しました。

### 2025/3/9 - CLI コマンド実行時のエラー修正

`python -m video_converter compress C:\Users\applejxd\Desktop\test.mp4` コマンドの実行時に発生するエラーを修正しました。以下の問題を解決しました：

1. `progress.py` ファイルの `tcp_handler` メソッドを呼び出す際に `PORT` パラメータを渡すように修正
2. `tcp_handler` メソッド内で、引数として受け取った `port` を使用するように修正
3. `utils.py` ファイルの `cli_wrapper` 関数内の `wrapper` 関数が `progress.run_with_tcp_pbar` の結果を返すように修正
4. `progress.py` ファイルの `run_with_tcp_pbar` 関数が `greenlet_ffmpeg.value` を返すように修正
5. `progress.py` ファイルの `monkey.patch_all()` のコメントアウトを解除

これらの修正により、CLI コマンドが正常に実行されるようになりました。

## 既知の問題

1. **`conveter.py` のファイル名のタイプミス**: ファイル名が `conveter.py` となっていますが、正しくは `converter.py` です。

2. **README.md の誤記**: README.md の使用方法セクションで、`python -m video_conveter open_window` となっていますが、正しくは `python -m video_converter gui` です。

3. **エラーハンドリングの不足**: ユーザーが無効なファイルパスを指定した場合や、FFmpeg の実行中にエラーが発生した場合のエラーハンドリングが不十分です。

## 今後の作業

### 短期的な作業（優先度: 高）

1. **既知のバグの修正**:
   - `conveter.py` のファイル名の修正
   - README.md の誤記の修正

2. **エラーハンドリングの改善**:
   - ユーザーが無効なファイルパスを指定した場合のエラーメッセージの改善
   - FFmpeg の実行中にエラーが発生した場合のエラーハンドリングの追加

### 中期的な作業（優先度: 中）

1. **テストの拡張**:
   - エラーケースのテストの追加
   - パフォーマンステストの追加

2. **ドキュメントの充実**:
   - API ドキュメントの追加
   - ユーザーガイドの追加

### 長期的な作業（優先度: 低）

1. **機能の拡張**:
   - 解像度変更機能の追加
   - フレームレート変更機能の追加
   - トリミング機能の追加
   - バッチ処理機能の追加

2. **GUI の改善**:
   - レイアウトの改善
   - 使いやすさの向上
   - テーマの追加

3. **プラグイン機構の実装**:
   - 新しい機能を簡単に追加できるプラグイン機構の実装
