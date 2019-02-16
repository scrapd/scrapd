"""Define the top-level cli command."""
import asyncio
import logging
import os
import sys

import click
from loguru import logger

from scrapd import config
from scrapd.cli.base import AbstractCommand
from scrapd.core import apd
from scrapd.core.formatter import Formatter
from scrapd.core.version import detect_from_metadata

# Set the project name.
APP_NAME = 'scrapd'

# Retrieve the project version from packaging.
__version__ = detect_from_metadata(APP_NAME)


# pylint: disable=unused-argument
#   The arguments are used via the `self.args` dict of the `AbstractCommand` class.
@click.group()
@click.version_option(version=__version__)
@click.option('-v', '--verbose', count=True, help='adjust the log level')
@click.pass_context
def cli(ctx, verbose):  # noqa: D403
    """
    ScrAPD main command.

    The log level can be adjusted by adding/removing `-v` flags:

    * None: Initial log level is WARNING.
    * -v: INFO
    * -vv: DEBUG
    * -vvv: TRACE

    For 2 `-v` and more, the log format also changes from compact to verbose.
    """
    ctx.obj = {**ctx.params}
    ctx.auto_envvar_prefix = 'VZ'

    # Load defaults from configuration file if any.
    cfg_path = os.path.join(click.get_app_dir(APP_NAME), APP_NAME + '.conf')
    cfg = cfg_path if os.path.exists(cfg_path) else None
    ctx.default_map = config.load(cfg, with_defaults=True, validate=True)

    # Configure logger.
    INITIAL_LOG_LEVEL = logging.WARNING
    LOG_FORMAT_COMPACT = "<level>{message}</level>"
    LOG_FORMAT_VERBOSE = "<level>{time:YYYY-MM-DDTHH:mm:ssZZ} {name}:{line:<4} {message}</level>"
    log_level = max(INITIAL_LOG_LEVEL - verbose * 10, 0)
    log_format = LOG_FORMAT_VERBOSE if log_level < logging.INFO else LOG_FORMAT_COMPACT

    # Remove any predefined logger.
    logger.remove()

    # Set the log colors.
    logger.level('ERROR', color='<red><bold>')
    logger.level('WARNING', color='<yellow>')
    logger.level('SUCCESS', color='<green>')
    logger.level('INFO', color='<cyan>')
    logger.level('DEBUG', color='<blue>')
    logger.level('TRACE', color='<magenta>')

    # Add the logger.
    logger.add(sys.stderr, format=log_format, level=log_level, colorize=True)


@click.command()
@click.option('--count', count=True, help='only count the number of results')
@click.option(
    '-f',
    '--format',
    type=click.Choice(['csv', 'gsheets', 'json', 'python']),
    default='csv',
    help='specify output format',
    show_default=True,
)
@click.option('--from', 'from_', help='start date')
@click.option('--gcontributors', help='comma separated list of contributors')
@click.option('--gcredentials', type=click.Path(), help='path of the google credentials file')
@click.option('--pages', default=-1, help='number pages to process')
@click.option('--to', help='end date')
@click.pass_context
# pylint: disable=W0622
def retrieve(ctx, count, format, from_, gcontributors, gcredentials, pages, to):
    """
    Retrieve APD's traffic fatality reports.

    The `retrieve` command allows you to fetch APD's traffic fatality reports in numerous formats and to tweak the
    results by specifying simple options.

    Available formats are: `CSV`, `JSON`, `Google Sheets` and `Python`.

    If `gsheets` is selected, you must also specify the path of the credentials file using the `--gcredentials` flag,
    and the list of contributors to your document with `--gcontributors`. Contributors are defined as a comma separated
    list of `<account>:<type>:<role>`, for instance `'alice@gmail.com:user:owner,bob@gmail.com:user:writer'`.

    * Valid account types are: `user`, `group`, `domain`, `anyone`.
    * Valid roles: `owner`, `writer`, `reader`.

    If the `count` option is used, the format is ignored. `count` simply returns the number of reports within the
    specified time range.

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
    """
    command = Retrieve(ctx.params, ctx.obj)
    command.execute()


class Retrieve(AbstractCommand):
    """Retrieve APD's traffic fatality reports."""

    def _execute(self):
        """Define the internal execution of the command."""
        # Check the params.
        self.check_params()

        # Collect the results.
        results, _ = asyncio.run(apd.async_retrieve(
            self.args['pages'],
            self.args['from_'],
            self.args['to'],
        ))
        result_count = len(results)
        logger.info(f'Total: {result_count}')

        # Get the format and print the results.
        format_ = 'count' if self.args['count'] else self.args['format'].lower()
        formatter = Formatter(format_)
        formatter.print(results)

    def check_params(self):
        """
        Raise an exception if a custom parameters is invalid or missing.

        This is to avoid collecting all the data then failing due to a missing parameter.
        """
        if self.args['format'].lower() == 'gsheets':
            if not self.args.get('gcredentials'):
                raise click.ClickException('Google credentials are required.')
            if not self.args.get('gcontributors'):
                raise click.ClickException('At least 1 contributor is required.')


cli.add_command(retrieve)
