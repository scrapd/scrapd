Testing
=======

How to test the regexes
-----------------------

.. code:: bash

  cd tests/data
  curl -sLO http://austintexas.gov/news/traffic-fatality-72-1
  export FIELD="Date:"
  grep -h -e "${FIELD}" -C 1 traffic-fatality-* | pbcopy
  open https://regex101.com/


Paste the result there, choose python, and work on your regex.
