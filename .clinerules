# Python ライブラリ構築の規約

## 0. 実装の方針

- **重要：ACT モードで同じ箇所の修正に2回失敗する場合は PLAN モードで方針を再検討**
- **重要：`tests` フォルダが存在する場合はすべての実行が True になってから完了**

## 1. 目的と設計の理解（PLAN モード）

- このライブラリが何を目的とするか把握
- 使用するライブラリを把握

## 2. 環境構築（ACT モード）

- 仮想環境の規約
  - `venv` で環境構築する。仮想環境作成先は `.venv`。
  - 存在しない場合は `py -3.11 -m venv .venv` で作成
  - 存在する場合はスクリプト実行・ライブラリインストール前に必ず `.\.venv\Scripts\Activate.ps1`
- ライブラリの仕様は `pyproject.toml` に記載

## 3. 実装（ACT モード）

- コメントの規約
  - docstring は sphinx-notypes スタイル
  - 関数定義には必ず type hinting を記載
  - 記載例：

    ```python
    def add(a: int, b: int) -> int:
        """
        数値を加算する関数。

        :param a: 加算する最初の数
        :param b: 加算する2番目の数
        :return: 2つの数の合計
        """
        return a + b
    ```

- スタイルの規約
  - formatter は black, linter は flake8
  - formatter, linter の error と warning は解決するまで解決
- テストの規約
  - `tests` フォルダにテストコードを配置し、`pytest` で実行
  - テストコードは `pytest` で実行してすべてのテストが True になるまで修正
