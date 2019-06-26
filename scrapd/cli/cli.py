"""Define the top-level cli command."""
import asyncio
import logging
import sys

import click
from loguru import logger

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
@click.version_option(version=__version__)
@click.command()
@click.option('-a', '--attempts', type=click.INT, default=3, help='number of attempts per report', show_default=True)
@click.option('-b', '--backoff', type=click.INT, default=3, help='initial backoff time (second)', show_default=True)
@click.option(
    '-f',
    '--format',
    'format_',
    type=click.Choice(sorted(Formatter.formatters)),
    default='json',
    help='specify output format',
    show_default=True,
)
@click.option('--from', 'from_', help='start date')
@click.option('--pages', default=-1, help='number pages to process')
@click.option('--to', help='end date')
@click.option('-v', '--verbose', count=True, help='adjust the log level')
@click.pass_context
def cli(ctx, attempts, backoff, format_, from_, pages, to, verbose):  # noqa: D403
    """Retrieve APD's traffic fatality reports."""
    ctx.obj = {**ctx.params}
    ctx.auto_envvar_prefix = 'VZ'

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

    # Prepare the command.
    command = Retrieve(ctx.params, ctx.obj)
    command.execute()


class Retrieve(AbstractCommand):
    """Retrieve APD's traffic fatality reports."""

    def _execute(self):
        """Define the internal execution of the command."""
        # Collect the results.
        results, _ = asyncio.run(
            apd.async_retrieve(
                self.args['pages'],
                self.args['from_'],
                self.args['to'],
                self.args['attempts'],
                self.args['backoff'],
            ))
        result_count = len(results)
        logger.info(f'Total: {result_count}')

        # Get the format and print the results.
        format_ = self.args['format_'].lower()
        formatter = Formatter(format_)
        formatter.print(results)
