"""Base class for all the `processor-cli` commands."""
import abc
import sys

from loguru import logger


class AbstractCommand:
    """Base class for the commands."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, command_args=None, global_args=None):
        """
        Initialize the commands.

        :param command_args: arguments of the command
        :param global_args: arguments of the program
        """
        # Store the global arguments.
        self.global_args = global_args or {}

        # Store the command arguments.
        self.args = command_args or {}

        # Set display parameters.
        self.data = []
        self.headers = []

    def execute(self):
        """Execute the command."""
        try:
            sys.exit(self._execute())
        except Exception as e:
            logger.exception(e)
            sys.exit(1)

    @abc.abstractmethod
    def _execute(self):
        """Define the internal execution of the command."""
        raise NotImplementedError
