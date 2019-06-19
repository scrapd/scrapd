.. include:: ../../.github/CONTRIBUTING.rst

Developer setup
---------------

You will need Python 3 and `nox`::

  pip3 install --user nox

Setup a local dev environment::

  nox --envdir .
  source venv/bin/activate

Run the CI tasks locally ::

  nox -s ci

Use `nox --list` to see all the available targets.

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
