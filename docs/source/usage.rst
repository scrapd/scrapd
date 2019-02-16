Detailed usage
==============

.. click:: scrapd.cli.cli:cli
   :prog: scrapd
   :show-nested:

docker
------

In addition to installing the Python package, you can also use the docker container.

.. code-block:: bash

  docker pull rgreinho/scrapd

The syntax is identical to the commands described above, simply use the `docker run` command before.

.. code-block:: bash

  docker run --rm -it \
    rgreinho/scrapd \
      -v \
      retrieve \
      --from "Feb 1 2019"

If you intend to export the results to Google Sheets, you must also mount your credential file.
It is a good practice to mount it as read-only.

.. code-block:: bash

  docker run --rm -it \
    -v ${HOME}/.config/scrapd/gsheet-credentials.json:/usr/src/app/creds.json:ro \
    rgreinho/scrapd \
      -v \
      retrieve \
      --from "Feb 1 2019" \
      --format gsheets \
      --gcredentials creds.json \
      --gcontributors "remy.greinhofer@gmail.com:user:writer"
