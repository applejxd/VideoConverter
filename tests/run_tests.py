"""
テストを実行するスクリプト
"""

import sys
import unittest
from pathlib import Path


def run_tests():
    """すべてのテストを実行する"""
    # テストディレクトリを取得
    test_dir = Path(__file__).parent
    
    # テストディレクトリをPythonパスに追加
    sys.path.insert(0, str(test_dir.parent))
    
    # テストを検出して実行
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(test_dir), pattern="test_*.py")
    
    # テスト結果を表示
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 終了コードを設定（テストが失敗した場合は1、成功した場合は0）
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())
