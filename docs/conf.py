"""Sphinx configuration for DC3 Model."""

from __future__ import annotations

import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "DC3 Model"
author = "Ojo Patrick Duke"
copyright = "2026, Ojo Patrick Duke"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
]

autosummary_generate = True
autodoc_typehints = "description"
autodoc_member_order = "bysource"
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_title = "DC3 Model"
html_show_sourcelink = True
html_sidebars = {
    "**": ["dc3-sidebar.html"],
}

html_theme_options = {
    "logo": {
        "text": "DC3 Model",
    },
    "navbar_align": "left",
    "navbar_start": ["navbar-logo"],
    "navbar_center": ["navbar-nav"],
    "navbar_end": ["theme-switcher", "navbar-icon-links"],
    "show_toc_level": 2,
    "navigation_depth": 3,
    "collapse_navigation": True,
    "show_nav_level": 1,
    "header_links_before_dropdown": 4,
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink"],
    "icon_links": [
        {
            "name": "Documentation",
            "url": "index.html",
            "icon": "fa-solid fa-book",
        },
    ],
}

version_json = os.getenv("DC3_DOCS_VERSION_JSON")
if version_json:
    html_theme_options["switcher"] = {
        "json_url": version_json,
        "version_match": os.getenv("READTHEDOCS_VERSION", release),
    }
    html_theme_options["navbar_end"] = [
        "version-switcher",
        "theme-switcher",
        "navbar-icon-links",
    ]

github_user = os.getenv("DC3_GITHUB_USER")
github_repo = os.getenv("DC3_GITHUB_REPO")
github_version = os.getenv("DC3_GITHUB_VERSION", "main")
if github_user and github_repo:
    html_theme_options["use_edit_page_button"] = True
    html_context = {
        "github_user": github_user,
        "github_repo": github_repo,
        "github_version": github_version,
        "doc_path": "docs",
    }
else:
    html_context = {}

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

myst_enable_extensions = [
    "colon_fence",
]
