Detailed usage
==============

.. click:: scrapd.cli.cli:cli
   :prog: scrapd

The command allows you to fetch APD's traffic fatality reports in numerous formats and to tweak the
results by specifying simple options.

Available formats are:

* `Count`: is a special format which simply counts the number of fatalities within the time range.
* `CSV`: is a delimited text file that uses a comma to separate values.
* `JSON`: is an open-standard file format that uses human-readable text to transmit data
  objects consisting of attribute–value pairs and array data types.
* `Python`: displays the data in a way that is directly usable in Python.

`attempts` defines the maximum number of attempts to parse a report before failing.

`backoff` defines the initial wait time, in seconds, between 2 retries. This time is then multiplied by 2 for each retry
(3s, then 6s, then 12s, etc.).

`page` is a way to limit the number of results by specifying of many APD news pages to parse. For instance, using
`--pages 5` means parsing the results until the URL https://austintexas.gov/department/news/296?page=4 is reached.
The results of the specified page are included. In that case, the valid results of the 5th page will be included.

The `from` and `to` options allow you to specify dates to filter the results. The values you define for these
bounderies will be included in the results. Now there are a few rules:

* `from`

    * omitting `from` means using `Jan 1 1` as the start date.
    * | in the `from` date, the **first** day of the month is used by default. `Jan 2019` will be interpreted as
      | `Jan 1 2019`.

* `to`

    * omiting `to` means using `Dec 31 9999` as the end date.
    * | in the `to` date, the **last** day of the month is used by default. `Jan 2019` will be interpreted as
      | `Jan 31 2019`.

* `both`

    * | only using the year will be replaced by the current day and month of the year you specified.
      | `2017` will be interpreted as `Jan 20 2017`.

The log level can be adjusted by adding/removing `-v` flags:

  * None: Initial log level is WARNING.
  * -v: INFO
  * -vv: DEBUG
  * -vvv: TRACE

For 2 `-v` and more, the log format also changes from compact to verbose.

docker
------

In addition to installing the Python package, you can also use the
[docker container](https://hub.docker.com/r/scrapd/scrapd).

.. code-block:: bash

  docker pull scrapd/scrapd

The syntax is identical to the commands described above, simply use the `docker run` command before.

.. code-block:: bash

  docker run --rm -it scrapd/scrapd -v --from "Feb 1 2019"
