# Configuration file for the Sphinx documentation builder.

# -- Project information
import os
import sys
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../..'))


project = 'gmft'
copyright = '2024, conjunct'
author = 'conjunct'

release = '0.4'
version = '0.4.0rc1'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
]

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# autodoc_default_options = {
#     'imported-members': True,
# }

autodoc_mock_imports = ['transformers', 'PIL', 'numpy', 'torch', 'matplotlib', 'pandas', 'pypdfium2', 'img2table'] # , 'torch', 'numpy', 'pandas']

# -- Options for HTML output

html_theme = 'sphinx_rtd_theme'

# -- Options for EPUB output
epub_show_urls = 'footnote'

# def setup(app):
#     app.add_css_file('custom.css')
    
html_static_path = ['_static']
html_css_files = ['custom.css']

# autosummary_generate = False
autoclass_content = 'both'