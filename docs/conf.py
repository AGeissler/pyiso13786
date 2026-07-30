# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import datetime
import os
import sys
from pathlib import Path

import pyvista
from pyvista.plotting.utilities.sphinx_gallery import DynamicScraper
from sphinx_gallery.sorting import FileNameSortKey

ROOT = Path(__file__).resolve().parents[1]

SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SRC = ROOT / "src/ISO_13786"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Manage errors
pyvista.set_error_output_file("errors.txt")
# Ensure that offscreen rendering is used for docs generation
pyvista.OFF_SCREEN = True  # Not necessary - simply an insurance policy
# Preferred plotting style for documentation
pyvista.set_plot_theme("document")

# necessary when building the sphinx gallery
pyvista.BUILDING_GALLERY = True
os.environ["PYVISTA_BUILDING_GALLERY"] = "true"

# ISO_13786: turn off logging if set to "false".
os.environ["ISO_13786_VERBOSE"] = "false"

# -- Project information -----------------------------------------------------
project = "ISO_13786"
year = datetime.date.today().year
copyright = f"2026-{year}, Achim Geissler"
author = "Achim Geissler"
release = "3.0.1"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_inline_tabs",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx_gallery.gen_gallery",
    "code_include.extension",
    "myst_parser",
    "matplotlib.sphinxext.plot_directive",
    "pyvista.ext.plot_directive",
    "pyvista.ext.viewer_directive",
]
myst_enable_extensions = [
    "deflist",
    "smartquotes",
]
source_suffix = {
    ".rst": "restructuredtext",
}
sphinx_gallery_conf = {
    "examples_dirs": ["../examples"],
    "gallery_dirs": ["examples"],
    "image_scrapers": (DynamicScraper(), "matplotlib"),
    "download_all_examples": False,
    "remove_config_comments": True,
    "reset_modules_order": "both",
    "filename_pattern": "ex.*\\.py",
    "backreferences_dir": None,
    "pypandoc": True,
    "capture_repr": ("_repr_html_",),
    "within_subsection_order": FileNameSortKey,
}
intersphinx_mapping = {
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
}

autosummary_generate = True

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# matplotlib plot directive
plot_include_source = True
plot_html_show_source_link = False
plot_html_show_formats = False
plot_formats = ["png"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "alabaster"
#html_theme = "pydata_sphinx_theme"
html_title = "ISO 13786"

html_static_path = ["_static"]
html_css_files = ["custom.css"]
