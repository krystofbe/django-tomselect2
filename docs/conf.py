import datetime
import os
import pathlib
import sys
from importlib.metadata import (
    version as get_version,
)

BASE_DIR = pathlib.Path(__file__).resolve(strict=True).parent.parent

# This is needed since django_tomselect2 requires django model modules
# and those modules assume that django settings is configured and
# have proper DB settings.
# Using this we give a proper environment with working django settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.testapp.settings")

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, str(BASE_DIR / "tests" / "testapp"))
sys.path.insert(0, str(BASE_DIR))


project = "django-tomselect2"
author = "Krystof Beuermann"
copyright = f"{datetime.datetime.now().year}, {author}"
# release = get_distribution("django_tomselect2").version # MODIFIED_2: Remove old line
release = get_version("django-tomselect2")  # MODIFIED_3: Use importlib.metadata.version
# version = ".".join(release.split(".")[:2]) # This line should be fine, but ensure 'release' is what you expect.
# Often, 'version' is the short X.Y version and 'release' is the full X.Y.Z version.
# If get_version gives you the full X.Y.Z, then:
_full_version = release
version = ".".join(_full_version.split(".")[:2])  # Example: "8.2" from "8.2.4..."

html_theme = "sphinx_rtd_theme"

master_doc = "index"  # default in Sphinx v2


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.napoleon",
    "sphinx.ext.inheritance_diagram",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx.ext.doctest",
    "myst_parser",
]

# Configure source file types
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
}

autodoc_default_flags = ["members", "show-inheritance"]
autodoc_member_order = "bysource"

inheritance_graph_attrs = {"rankdir": "TB"}
inheritance_node_attrs = {
    "shape": "rect",
    "fontsize": 14,
    "fillcolor": "gray90",
    "color": "gray30",
    "style": "filled",
}

inheritance_edge_attrs = {"penwidth": 0.75}
