# SPDX-FileCopyrightText: 2023 Filipe Laíns
#
# SPDX-License-Identifier: MIT

import ffy00.packaging


project = 'ffy00.packaging'
copyright = '2023, Filipe Laíns'
author = 'Filipe Laíns'
version = release = ffy00.packaging.__version__


extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx_autodoc_typehints',
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx_issues',
    'sphinxcontrib.spelling',
    'sphinxext.opengraph',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'importlib_metadata': ('https://importlib-metadata.readthedocs.io/en/latest/', None),
    'importlib_resources': ('https://importlib-resources.readthedocs.io/en/latest/', None),
}

templates_path = ['_templates']
exclude_patterns = []
default_role = 'any'
autoclass_content = 'both'

todo_include_todos = True

issues_github_path = f'FFY00/{project}'

html_theme = 'furo'
html_title = f'{project} {version}'

html_theme_options = {
    'light_css_variables': {
        'font-stack': (
            'system-ui,-apple-system,BlinkMacSystemFont,Segoe UI,'
            'Helvetica,Arial,sans-serif,Apple Color Emoji,Segoe UI Emoji'
        ),
    },
}

spelling_show_suggestions = True
spelling_warning = True

ogp_site_url = f'https://{project}.readthedocs.io'
ogp_site_name = f'{project} documentation'
