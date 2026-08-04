"""Sphinx configuration for the DC3 Model App documentation."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

project = "DC3 Model App"
author = "Ojo Patrick Duke"
copyright = "2026, Ojo Patrick Duke"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "pydata_sphinx_theme"
html_static_path = [str(ROOT / "docs" / "_static")]
html_css_files = ["custom.css"]
html_title = "DC3 Model App"
html_show_sourcelink = True
html_sidebars = {
    "**": ["app-sidebar.html"],
}

html_theme_options = {
    "logo": {
        "text": "DC3 Model App",
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
            "name": "Package Docs",
            "url": "http://localhost:8511",
            "icon": "fa-solid fa-cube",
        },
    ],
}

github_user = os.getenv("DC3_GITHUB_USER")
github_repo = os.getenv("DC3_GITHUB_REPO")
github_version = os.getenv("DC3_GITHUB_VERSION", "main")
if github_user and github_repo:
    html_theme_options["use_edit_page_button"] = True
    html_context = {
        "github_user": github_user,
        "github_repo": github_repo,
        "github_version": github_version,
        "doc_path": "app_docs",
    }
else:
    html_context = {}

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True

myst_enable_extensions = [
    "colon_fence",
]
