=============
Theming Guide
=============

For now the ``herobase module`` holds all templates, stylesheets and other theming related files.

Base CSS
========

First of all we use `Bootstrap <http://twitter.github.com/bootstrap/index.html>`_ as a kind of base stylesheet and design.
It comes with a lot of nice CSS classes and JS scripts. Especially the Forms, Buttons and Buttonbars look fancy
across all modern browsers. At the same time we use the grid-system only slightly modfied.

Bootstrap is located in ``src/herobase/static/bootstrap/`` and its CSS is linked per default by the ``base.html`` template.

LESS
==========

`Less <http://lesscss.org/>`_ is a Language for generating CSS. The Bootstrap CSS can be build from LESS sources,
which allows us changing colors and other variables easily.

In Bootstrap's LESS files we only touch ``bootstrap/less/variables.less``. You find all custom LESS code in
``src/herobase/static/less/custom.less``.

LESS Setup
----------

To customize the LESS files you need a LESS compiler. Basically LESS could be compiled by ``less.js`` directly in the browser.
Since such a build takes >4 sec on my (old) machine and it would be annoying to take care about consistent files,
this is nothing for the git repo, and we recommend the commandline tool ``lessc``.

First install the node package manager:

    $ sudo apt-get install npm

Afterwards install less and some bootstrap-dependencies:

    $ npm install -g less jshint recess uglify-js

Now you can compile Bootstrap with:

    $ lessc src/herobase/static/bootstrap/less/bootstrap.less > src/herobase/static/bootstrap/css/bootstrap.css

And our custom less:

    $ lessc src/herobase/static/less/custom.less > src/herobase/static/css/custom.css

Watchr Setup
------------

With `watchr <https://github.com/mynyml/watchr>`_ you can automatically rebuild a ``.less`` file every time you edit the file.
A watchr script for the above files is ``deploy/less.watchr``.

Install ``rubygems``:

    $ sudo apt-get install rubygems

And afterwards ``watchr``:

    $ gem install watchr

Run watchr-script in the project-root:

    $ watchr deploy/less.watchr
