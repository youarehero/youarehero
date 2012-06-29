========
How To's
========

How to edit the Documentation
=============================

The documentation is build with `sphinx <http://sphinx.pocoo.org/>`_,
see `sphinx tutorial <http://sphinx.pocoo.org/tutorial.html>`_.

**Sourcecode documentation** is build from
`python docstrings <http://epydoc.sourceforge.net/docstrings.html>`_ in the source itself.

**Other documentation**, like this document, is written in `reST <http://sphinx.pocoo.org/rest.html>`_
with additional `sphinx-syntax <http://sphinx.pocoo.org/markup/inline.html>`_,
espacially for internal links or ``cross-references``.

The documentation root dir is ``docs/``. The ``.rst``-files contain all custom documentation.
The most important elements are::

   Headlines
   =========

   paragraphs

   `links <url>`_

You can build your documentation code with::

   (env)$ docs/make html

In some cases use::

   (env)$ docs/make clean html

Afterwards open ``file:///<project_path>/docs/_build/html/index.html``, test your documentation
and commit your changes.
