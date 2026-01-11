# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "video-converter"
copyright = "2026, applejxd"
author = "applejxd"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",  # docstrings から自動的に API ドキュメントを生成
    "sphinx.ext.apidoc",  # 自動的にモジュールのドキュメントを生成
    "sphinx.ext.viewcode",  # ドキュメントからソースコードへのリンクを追加
    "sphinx.ext.inheritance_diagram",  # クラスの継承図を生成
    "sphinx.ext.graphviz",  # Graphviz を使って図を埋め込む
    "sphinx_mdinclude",  # Markdown 読み込みに対応
    "sphinx.ext.githubpages",  # GitHub Pages に公開するための補助ファイルを出力
]

templates_path = ["_templates"]
exclude_patterns = []

language = "en"

autoclass_content = "both"  # __init__() も出力
autodoc_typehints = "description"  # 型ヒントを有効化
autodoc_default_options = {
    "private-members": True,  # プライベートメソッドも出力
    "show-inheritance": True,  # 継承を表示
}

# sphinx-apidoc 自動実行
# see https://www.sphinx-doc.org/en/master/usage/extensions/apidoc.html
apidoc_modules = [
    {"path": "../../../src", "destination": "./api", "separate_modules": True},
]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# # LuaLaTeXを使用
# latex_engine = 'lualatex'
# # LaTeXドキュメントクラスとしてltjsbookを使用
# latex_docclass = {'manual': 'ltjsarticle'}

latex_preamble = R"""
\usepackage{xltxtra}
\setmainfont{TakaoMincho}
\setsansfont{TakaoGothic}
\setmonofont{TakaoGothic}
\XeTeXlinebreaklocale "ja"
"""
latex_elements = {
    "extraclassoptions": "openany",
}
