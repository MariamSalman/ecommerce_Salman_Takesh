import os
import sys
import sphinx_rtd_theme

# -- Path setup --------------------------------------------------------------

# Add the project's source directory to the sys.path to enable autodoc to find your modules
sys.path.insert(0, os.path.abspath('../'))

# -- Project information -----------------------------------------------------
project = 'Your Project Name'
author = 'Your Name'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',       # Automatic documentation generation
    'sphinx.ext.napoleon',      # Google-style docstrings
    'sphinx.ext.viewcode',      # View source code links in the docs
    'recommonmark',             # Support for Markdown files
]

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Use the Read-the-Docs theme
html_static_path = ['_static']

# -- Autodoc settings -------------------------------------------------------
autodoc_member_order = 'bysource'  # Order members by source order (not alphabetical)

# -- Other settings ---------------------------------------------------------
master_doc = 'index'  # The main entry point for Sphinx to generate documentation from
