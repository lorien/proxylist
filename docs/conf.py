html_theme = "sphinx_rtd_theme"
project = "proxylist"
copyright = "2015-2023, Gregory Petukhov"
author = "Gregory Petukhov"
release = "0.2.1"
extensions = [
    "myst_nb",
    "autoapi.extension",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
autoapi_dirs = ["../proxylist"]  # location to parse for API reference
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
