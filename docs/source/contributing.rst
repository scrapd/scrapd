.. include:: ../../.github/CONTRIBUTING.rst

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

.. _`invoke`: https://docs.pyinvoke.org/
.. _`nox`: https://nox.thea.codes/
