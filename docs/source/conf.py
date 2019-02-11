# -*- coding: utf-8 -*-
#
# ipypublish documentation build configuration file, created by
# sphinx-quickstart on Sat Jun  3 02:06:22 2017.
#
# http://www.sphinx-doc.org/en/master/usage/configuration.html
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import io
import urllib
import json
import shutil
import subprocess

import sphinx
from sphinx.application import Sphinx  # noqa

import ipypublish

on_rtd = os.environ.get('READTHEDOCS') == 'True'

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
needs_sphinx = '1.6'

# The master toctree document.
master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',  # TODO is this needed?
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
    # 'sphinx.ext.imgconverter'  # converts svg to pdf in latex output
    # TODO imgconverter failing (I guess for process.svg),
    'ipypublish.ipysphinx'
]


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
# source_suffix = {
#     '.rst': 'restructuredtext',
#     '.md': 'markdown',
#     '.ipynb': 'jupyter_notebook'
# }
# source_suffix = ['.rst', '.md', '.ipynb']

if sphinx.version_info[0:2] < (1, 8):
    source_parsers = {
        '.md': 'recommonmark.parser.CommonMarkParser',
        '.Rmd': 'ipypublish.ipysphinx.parser.NBParser'
    }
else:
    source_parsers = {
        '.md': 'recommonmark.parser.CommonMarkParser'
    }
    ipysphinx_jupytext = [".Rmd"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "build", "**.ipynb_checkpoints"]


# General information about the project.
project = u'ipypublish'
copyright = u'2017, Chris Sewell'
author = u'Chris Sewell'
description = ('Create quality publication and presentation'
               'directly from Jupyter Notebook(s)')

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = ipypublish.__version__
# The full version, including alpha/beta/rc tags.
release = ipypublish.__version__

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
# html_logo = '_static/doc_icon_100px.png'
html_favicon = '_static/doc_icon_32px.ico'

# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'ipypublishdoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'ipypublish.tex', u'ipypublish Documentation',
     u'Chris Sewell', 'manual'),
]

# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'ipypublish', u'ipypublish Documentation',
     [author], 1)
]

# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'ipypublish', u'IPyPublish',
     author, 'ipypublish', description,
     'Miscellaneous'),
]

# Numbered Elements
numfig = True
math_numfig = True
numfig_secnum_depth = 2
numfig_format: {'section': 'Section %s',
                'figure': 'Fig. %s',
                'table': 'Table %s',
                'code-block': 'Code Block %s'}
math_number_all = True
math_eqref_format = "Eq. {number}"  # TODO this isn't working

mathjax_config = {
    'TeX': {'equationNumbers': {'autoNumber': 'AMS', 'useLabelIds': True}},
}

# Napoleon Docstring settings
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True


# INTERSPHINX

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3.6', None),
    # 'numpy': ('http://docs.scipy.org/doc/numpy/', None),
    # 'scipy': ('http://docs.scipy.org/doc/scipy/reference/', None),
    # 'matplotlib': ('http://matplotlib.sourceforge.net/', None),
    # 'pandas': ('http://pandas.pydata.org/pandas-docs/stable/', None),
    # 'IPython': ('http://ipython.org/ipython-doc/stable/', None),
    'PIL': ('http://pillow.readthedocs.org/en/latest/', None),
    'nbconvert': ("http://nbconvert.readthedocs.io/en/latest/", None),
    'nbformat': ("http://nbformat.readthedocs.io/en/latest/", None),
    'tornado': ("https://www.tornadoweb.org/en/stable/", None),
    'traitlets': ("https://traitlets.readthedocs.io/en/stable/", None),
    'jinja': ('http://jinja.pocoo.org/docs/dev', None),
    # 'docutils': ("https://docutils.readthedocs.io/en/sphinx-docs", None),
    # # TODO docutils intersphinx
    # 'sphinx': ('http://www.sphinx-doc.org/en/latest/', None)
}

intersphinx_aliases = {
    ('py:class', 'nbconvert.preprocessors.base.Preprocessor'):
        ('py:class', 'nbconvert.preprocessors.Preprocessor'),
    ('py:class', 'nbformat.notebooknode.NotebookNode'):
        ('py:class', 'nbformat.NotebookNode'),
    ('py:class', 'traitlets.config.configurable.Configurable'):
        ('py:module', 'traitlets.config')
}

# Warnings to ignore when using the -n (nitpicky) option
# We should ignore any python built-in exception, for instance
nitpick_ignore = [('py:exc', 'ArithmeticError'), ('py:exc', 'AssertionError'),
                  ('py:exc', 'AttributeError'), ('py:exc', 'BaseException'),
                  ('py:exc', 'BufferError'), ('py:exc', 'DeprecationWarning'),
                  ('py:exc', 'EOFError'), ('py:exc', 'EnvironmentError'),
                  ('py:exc', 'Exception'), ('py:exc', 'FloatingPointError'),
                  ('py:exc', 'FutureWarning'), ('py:exc', 'GeneratorExit'),
                  ('py:exc', 'IOError'), ('py:exc', 'ImportError'),
                  ('py:exc', 'ImportWarning'), ('py:exc', 'IndentationError'),
                  ('py:exc', 'IndexError'), ('py:exc', 'KeyError'),
                  ('py:exc', 'KeyboardInterrupt'), ('py:exc', 'LookupError'),
                  ('py:exc', 'MemoryError'), ('py:exc', 'NameError'),
                  ('py:exc', 'NotImplementedError'), ('py:exc', 'OSError'),
                  ('py:exc', 'OverflowError'),
                  ('py:exc', 'PendingDeprecationWarning'),
                  ('py:exc', 'ReferenceError'), ('py:exc', 'RuntimeError'),
                  ('py:exc', 'RuntimeWarning'), ('py:exc', 'StandardError'),
                  ('py:exc', 'StopIteration'), ('py:exc', 'SyntaxError'),
                  ('py:exc', 'SyntaxWarning'), ('py:exc', 'SystemError'),
                  ('py:exc', 'SystemExit'), ('py:exc', 'TabError'),
                  ('py:exc', 'TypeError'), ('py:exc', 'UnboundLocalError'),
                  ('py:exc', 'UnicodeDecodeError'),
                  ('py:exc', 'UnicodeEncodeError'), ('py:exc', 'UnicodeError'),
                  ('py:exc', 'UnicodeTranslateError'),
                  ('py:exc', 'UnicodeWarning'), ('py:exc', 'UserWarning'),
                  ('py:exc', 'VMSError'), ('py:exc', 'ValueError'),
                  ('py:exc', 'Warning'), ('py:exc', 'WindowsError'),
                  ('py:exc', 'ZeroDivisionError'), ('py:obj', 'str'),
                  ('py:obj', 'list'),
                  ('py:obj', 'tuple'),
                  ('py:obj', 'int'),
                  ('py:obj', 'float'),
                  ('py:obj', 'bool'),
                  ('py:obj', 'Mapping'),
                  ('py:obj', 'MutableMapping'),
                  ('py:func', 'str.format'),
                  ('py:class', '_abcoll.MutableMapping'),
                  ('py:class',
                   'traitlets.config.configurable.LoggingConfigurable'),
                  ('py:class', 'docutils.nodes.Element'),
                  ('py:class', 'docutils.parsers.rst.Directive'),
                  ('py:class', 'docutils.transforms.Transform'),
                  ('py:class', 'docutils.parsers.rst.Parser'),
                  ('py:class', 'sphinx.parsers.RSTParser'),
                  ('py:obj', 'sphinx.application.Sphinx'),
                  ('py:exc', 'nbconvert.pandoc.PandocMissing')
                  ]

try:
    out = subprocess.check_output(["git", "branch"]).decode("utf8")
    current = next(line for line in out.split("\n") if line.startswith("*"))
    gitbranch = current.strip("*").strip()
except subprocess.CalledProcessError:
    gitbranch = None

# on rtd, returns e.g. (HEAD detached at origin/develop)
if gitbranch is not None and "develop" in gitbranch:
    gitpath = "blob/develop"
    binderpath = "develop"
else:
    gitpath = "blob/v{}".format(ipypublish.__version__)
    binderpath = "v{}".format(ipypublish.__version__)

ipysphinx_prolog = r"""
{{% set docname = env.doc2path(env.docname, base='docs/source') %}}

.. only:: html

    .. role:: raw-html(raw)
        :format: html

    .. nbinfo::

        | This page was generated from `{{{{ docname }}}}`__,
          with configuration: ``{{{{ env.config.ipysphinx_export_config }}}}``
        {{%- if docname.endswith('.ipynb') %}}
        | Interactive online version:
          :raw-html:`<a href="https://mybinder.org/v2/gh/chrisjsewell/ipypublish/{binderpath}?filepath={{{{ docname }}}}"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>`
        {{%- endif %}}

    __ https://github.com/chrisjsewell/ipypublish/{gitpath}/{{{{ docname }}}}

""".format(gitpath=gitpath, binderpath=binderpath)


def create_git_releases(app):

    this_folder = os.path.abspath(
        os.path.dirname(os.path.realpath(__file__)))

    git_history = urllib.request.urlopen(
        'https://api.github.com/repos/chrisjsewell/ipypublish/releases'
    ).read().decode('utf-8')
    # NOTE on vscode this could fail with urllib.error.HTTPError
    git_history_json = json.loads(git_history)
    # NOTE on vscode this was failing unless encoding='utf8' was present
    with io.open(os.path.join(this_folder, 'releases.md'),
                 'w', encoding="utf8") as f:
        f.write('# Releases\n')
        f.write('\n')
        for i, r in enumerate(git_history_json):
            if r['tag_name'].split(".")[-1] == "0":
                level = '## '
            elif i == 0:
                f.write("## Current Version\n")
                level = '### '
            else:
                level = '### '
            subtitle = level + ' '.join([r['tag_name'],
                                         '-', r['name'], '\n'])
            f.write(subtitle)
            f.write('\n')
            for line in r['body'].split('\n'):
                f.write(' '.join([line, '\n']))
            f.write('\n')


def add_intersphinx_aliases_to_inv(app):
    """see https://github.com/sphinx-doc/sphinx/issues/5603"""
    from sphinx.ext.intersphinx import InventoryAdapter
    inventories = InventoryAdapter(app.builder.env)

    for alias, target in app.config.intersphinx_aliases.items():
        alias_domain, alias_name = alias
        target_domain, target_name = target
        try:
            found = inventories.main_inventory[target_domain][target_name]
            try:
                inventories.main_inventory[alias_domain][alias_name] = found
            except KeyError:
                continue
        except KeyError:
            continue


def run_apidoc(app):
    """ generate apidoc 

    See: https://github.com/rtfd/readthedocs.org/issues/1139
    """
    # get correct paths
    this_folder = os.path.abspath(
        os.path.dirname(os.path.realpath(__file__)))
    api_folder = os.path.join(this_folder, "api")
    # module_path = ipypublish.utils.get_module_path(ipypublish)
    module_path = os.path.normpath(
        os.path.join(this_folder, "../../"))
    ignore_setup = os.path.normpath(
        os.path.join(this_folder, "../../setup.py"))
    ignore_tests = os.path.normpath(
        os.path.join(this_folder, "../../ipypublish/tests"))
    if os.path.exists(api_folder):
        shutil.rmtree(api_folder)
    os.mkdir(api_folder)

    argv = ["--separate", "-o", api_folder,
            module_path, ignore_setup, ignore_tests]

    try:
        # Sphinx 1.7+
        from sphinx.ext import apidoc
    except ImportError:
        # Sphinx 1.6 (and earlier)
        from sphinx import apidoc
        argv.insert(0, apidoc.__file__)

    apidoc.main(argv)

    # we don't use this
    if os.path.exists(os.path.join(api_folder, "modules.rst")):
        os.remove(os.path.join(api_folder, "modules.rst"))


def get_version():
    """alternative to getting directly"""
    import re
    this_folder = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    init_file = os.path.join(this_folder, "../../ipypublish/__init__.py")
    with open(init_file) as fobj:
        content = fobj.read()

    match = re.match(
        "\\_\\_version\\_\\_\\s*\\=\\s*[\\'\\\"]([0-9\\.]+)", content)
    if not match:
        raise IOError("couldn't find __version__ in: {}".format(init_file))
    return match.group(1)


def setup(app):
    # type: (Sphinx) -> dict
    """
    extension for sphinx, for custom config
    """

    # app.connect('autodoc-skip-member', skip_deprecated)

    # add aliases for intersphinx
    app.add_config_value('intersphinx_aliases', {}, 'env')
    app.connect('builder-inited', run_apidoc)
    app.connect('builder-inited', create_git_releases)
    app.connect('builder-inited', add_intersphinx_aliases_to_inv)
