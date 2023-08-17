# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

from baecon import __version__

# import pydata_sphinx_theme

# sys.path.insert(0, os.path.abspath("../../src"))
# sys.path.append('../../src')
# sys.path.append('C:\\Users\\walsworth1\\Documents\\Jupyter_Notebooks\\baecon\\docs')

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Baecon"
copyright = "2023, Kevin S. Olsson"
author = "Kevin S. Olsson"
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    #'groundwork-sphinx-theme',
]

templates_path = ["_templates"]
exclude_patterns = []

todo_include_todos = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = [
    "css/custom.css",
]

html_theme_options = {
    "show_toc_level": 2,
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink"],
}


pygments_style = "sphinx"
pygments_dark_style = "monokai"
