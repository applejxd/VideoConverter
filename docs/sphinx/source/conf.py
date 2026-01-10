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
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx_mdinclude",
    "sphinx.ext.graphviz",
    "sphinx.ext.inheritance_diagram",
]

templates_path = ["_templates"]
exclude_patterns = []

language = "en"

# 型ヒントを有効
autodoc_typehints = "description"
# __init__()も出力
autoclass_content = "both"
autodoc_default_options = {
    # プライベートメソッドも出力
    "private-members": True,
    # 継承を表示
    "show-inheritance": True,
}

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
