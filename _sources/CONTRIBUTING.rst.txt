Contributing
============

Instructions for contributors
-----------------------------

We are interested in various different kinds of improvement for ScrAPD. Please feel free to raise an `Issue`_ if you
would like to work on something major to ensure efficient collaboration and avoid duplicate effort.

Guidelines
^^^^^^^^^^

* Use the provided templates to file an `Issue`_ or a `Pull Request`_.

* Create a topic branch from where you want to base your work.

* We follow the `Open Stack Coding Guidelines`_.

* For formatting the files properly, please use `YAPF`_. In the root directory of the project, run the following
  command: `make format`.

* Make sure you added tests to validate your changes.

* Run all the tests to ensure nothing else was accidentally broken.

* Commit messages must start with a capitalized and short summary (max. 50 chars) written in the imperative, followed by
  an optional, more detailed explanatory text which is separated from the summary by an empty line.

* Commit messages should follow best practices, including explaining the context of the problem and how it was solved,
  including in caveats or follow up changes required. They should tell the story of the change and provide readers
  understanding of what led to it. Please refer to `How to Write a Git Commit Message`_ for more details.

* If your `Pull Request`_ is a work in progress, create it as a `Draft Pull Request`_.

* Any `Pull Request`_ inactive for 28 days will be automatically closed. If you need more time to work on it, ask
  maintainers, to add the appropriate label to it. Use the `@scrapd/scrapper` mention in the comments.

* Unless explicitly asked, `Pull Request`_ which don't pass all the CI checks will not be reviewed.
  Use the `@scrapd/scrapper` mention in the comments if to ask maintainers to help you.

Commit example
""""""""""""""

.. code-block:: bash

  Use Docker Hub build environment values

  Uses the Docker Hub build environment values in order to ensure the
  correct version of ScrAPD is installed into the image.

  Fixes scrapd/scrapd#54

The following commit is a good example as:

1. The fist line is a short description and starts with an imperative verb
2. The first paragraph describes why this commit may be useful
3. The last line points to an existing issue and will automatically close it.

Formatting your code
^^^^^^^^^^^^^^^^^^^^

There is also a lot of YAPF plugins available for different editors. Here are a few:

  * `atom.io <https://atom.io/packages/python-yapf>`_
  * `emacs <https://github.com/paetzke/py-yapf.el>`_
  * `sublime text <https://github.com/jason-kane/PyYapf>`_
  * `vim <https://github.com/google/yapf/blob/master/plugins/yapf.vim>`_

Developer setup
---------------

You will need Python 3 `invoke`_ and `nox`_::

  pip3 install --user nox invoke

Setup a local dev environment::

  inv
  source venv/bin/activate

Run the CI tasks locally ::

  inv nox -s ci

Use `inv --list`  and `inv nox` to see all the available targets.

The `nox` tasks can be invoked by running  either:

* `inv nox -s {task}`, for instance `inv nox -s test`
* or directly with `nox -s test`

Testing
-------

How to test the regexes
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

  cd tests/data
  curl -sLO http://austintexas.gov/news/traffic-fatality-72-1
  export FIELD="Date:"
  grep -h -e "${FIELD}" -C 1 traffic-fatality-* | pbcopy
  open https://regex101.com/


Paste the result there, choose python, and work on your regex.


Profiling
---------

The profiling for the project is mostly done using `pyinstrument`_

You can use the nox task to run the profiler automatically::

  inv profile

Additionally, you can also generate a flame graph with `py-spy`_. It requires root permissions, therefore must be run
with sudo and will prompt you for your password::

  inv flame-graph


.. _`Draft Pull Request`: https://github.blog/2019-02-14-introducing-draft-pull-requests/
.. _`How to Write a Git Commit Message`: http://chris.beams.io/posts/git-commit
.. _`Issue`: https://github.com/scrapd/scrapd/issues
.. _`Open Stack Coding Guidelines`: https://docs.openstack.org/charm-guide/latest/coding-guidelines.html
.. _`Pull Request`: https://github.com/scrapd/scrapd/pulls
.. _`YAPF`: https://github.com/google/yapf
.. _`invoke`: https://docs.pyinvoke.org/
.. _`nox`: https://nox.thea.codes/
.. _`pyinstrument`: https://github.com/joerick/pyinstrument
.. _`py-spy`: https://github.com/benfred/py-spy
