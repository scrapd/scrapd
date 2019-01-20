"""Define the top-level cli command."""
import asyncio
import csv
import json
import logging
import os
import pprint
import sys

import click
from loguru import logger

from scrapd import config
from scrapd.cli.base import AbstractCommand
from scrapd.core import apd
from scrapd.core.constant import Fields
from scrapd.core.version import detect_from_metadata

# Set the project name.
APP_NAME = 'scrapd'

# Retrieve the project version from packaging.
__version__ = detect_from_metadata(APP_NAME)


# pylint: disable=unused-argument
#   The arguments are used via the `self.args` dict of the `AbstractCommand` class.
@click.group()
@click.version_option(version=__version__)
@click.option('-v', '--verbose', count=True, help='defines the log level')
@click.pass_context
def cli(ctx, verbose):
    """Manage CLI commands."""
    ctx.obj = {**ctx.params}
    ctx.auto_envvar_prefix = 'VZ'

    # Load defaults from configuration file if any.
    cfg_path = os.path.join(click.get_app_dir(APP_NAME), APP_NAME + '.conf')
    cfg = cfg_path if os.path.exists(cfg_path) else None
    ctx.default_map = config.load(cfg, with_defaults=True, validate=True)

    # Configure logger.
    # The log level gets adjusted by adding/removing `-v` flags:
    #   None    : Initial log level is WARNING.
    #   -v      : INFO
    #   -vv     : DEBUG
    #   -vvv    : TRACE
    # For 2 `-v` and more, the log format also changes from compact to verbose.
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
@click.option(
    '-f',
    '--format',
    type=click.Choice(['python', 'json', 'csv']),
    default='csv',
    help='specify output format',
    show_default=True,
)
@click.option('--pages', default=-1, help='number pages to process')
@click.option('--from', 'from_', help='start date')
@click.option('--to', help='end date')
@click.pass_context
# pylint: disable=W0622
def retrieve(ctx, format, pages, from_, to):
    """Retrieve APD's traffic fatality reports."""
    command = Retrieve(ctx.params, ctx.obj)
    command.execute()


class Retrieve(AbstractCommand):
    """Retrieve APD's traffic fatality reports."""

    def _execute(self):
        """Define the internal execution of the command."""
        # Collectr the results.
        results = asyncio.run(apd.async_retrieve(
            self.args['pages'],
            self.args['from_'],
            self.args['to'],
        ))
        logger.info(f'Total: {len(results)}')

        # Display them.
        output_format = self.args['format'].lower()
        if output_format == 'python':
            pp = pprint.PrettyPrinter(indent=2)
            pp.pprint(results)
        elif output_format == 'json':
            print(json.dumps(results, sort_keys=True, indent=2))
        else:
            # Write CSV file.
            CSVFIELDS = [
                Fields.CRASHES,
                Fields.CASE,
                Fields.DATE,
                Fields.TIME,
                Fields.LOCATION,
                Fields.FIRST_NAME,
                Fields.LAST_NAME,
                Fields.ETHNICITY,
                Fields.GENDER,
                Fields.DOB,
                Fields.AGE,
                Fields.LINK,
            ]
            writer = csv.DictWriter(sys.stdout, fieldnames=CSVFIELDS, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(results)


cli.add_command(retrieve)
