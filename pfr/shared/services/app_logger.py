"""
Setup logging outputs, format and levels for the application.
"""
import logging
from os.path import isdir, join
from os import mkdir
from logging.handlers import TimedRotatingFileHandler
from pydantic import BaseModel, Field, ValidationError


class AppLoggerParameters(BaseModel):
    """
    Keep and validate the parameters for the application logger. A pydantic
    model is used to validate the entries on init.

    Parameters
    ----------
    path: str
        Output folder of the logs

    file:
       Name of the output file

    level:
        Alert level to log

    file_count:
        Number of old log files to keep
    """

    path: str = Field(min_length=1, max_length=255, alias="LOG_PATH")
    file: str = Field(min_length=1, max_length=65, alias="LOG_FILE")
    level: int = Field(gt=0, alias="LOG_LEVEL")
    file_count: int = Field(gt=0, alias="LOG_FILECOUNT")


class AppLogger:
    """Setup logging outputs, format and levels for the application.

    Note
    ----
    Logs are outputed into files and on the console stream. The files
    are rotated on a daily basis

    Attributes
    ----------
    _parameters : RecordFetcherParameters
        The inside class object defining redis options

    _logger : logging.Logger
        local Logger.
    """

    def __init__(self, config: dict) -> None:
        """This function is used to ensure the presence and coherence
        of configuration parameters needed by the logger.

        Parameters
        ----------
        config
            The configuration dictionary of the application.

        Returns
        -------
        None

        Exceptions
        -------
        RuntimeError
            Something went wrong during setup process.

        """
        self._logger = logging.getLogger(__name__)

        if not isinstance(config, dict):
            self._logger.critical(
                exc_info=True,
                msg="The configuration given to the"
                    f"logger is not of dict type : {type(config)}"
            )
            raise RuntimeError("Bad configuration type")

        try:
            self._parameters = AppLoggerParameters(**config)
        except ValidationError as e:
            self._logger.critical(
                exc_info=True,
                msg=f"Faulty parameter into the logger's configuration : {e}."
            )
            raise RuntimeError("Faulty configuration param") from e

        if not self.check_log_folder():
            raise RuntimeError("Missing log folder")

        self._setup_logger()

    def check_log_folder(self) -> bool:
        """Check if the log folder exist. If not create the folder.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            if not isdir(self._parameters.path):
                mkdir(self._parameters.path)
        except OSError as e:
            self._logger.critical(
                exc_info=True,
                msg=f"An error occured when checking / creating the log folder : {e}."
            )
            return False
        return True

    def _setup_logger(self) -> bool:
        """Create the handlers used to output logs into files and on the
        console. Add them to the root logger to unify loggers behaviours.

        Parameters
        ----------
        None

        Returns
        -------
        bool
            If an error arise during setuip procedure, return False.
            If everytihng is fine, return True.
        """
        try:
            file_handler = TimedRotatingFileHandler(
                join(self._parameters.path, self._parameters.file),
                when="midnight",
                interval=1,
                backupCount=self._parameters.file_count,
                encoding=None,
                delay=False,
                utc=False,
                atTime=None,
                errors=None,
            )
            stream_handler = logging.StreamHandler()
        except Exception as e:
            self._logger.critical(
                exc_info=True,
                msg=f"Unexpected error occured when creating handlers : {e}."
            )
            raise RuntimeError("Error Handler Creation") from e

        file_formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )

        try:
            file_handler.setFormatter(file_formatter)
            stream_handler.setFormatter(file_formatter)
        except Exception as e:
            self._logger.critical(
                exc_info=True,
                msg=f"Unexpected error occured when setting formatters : {e}."
            )
            raise RuntimeError("Failed Setting Formatter") from e

        try:
            logging.getLogger().setLevel(self._parameters.level)
        except (ValueError, TypeError) as e:
            self._logger.critical(
                exc_info=True,
                msg=f"Unexpected error occured when setting log level : {e}."
            )
            raise RuntimeError("Failed Set Level") from e

        try:
            logging.getLogger().addHandler(file_handler)
            logging.getLogger().addHandler(stream_handler)
        except Exception as e:
            self._logger.critical(
                exc_info=True,
                msg=f"Unexpected error occured  when adding handlers to logger : {e}."
            )
            raise RuntimeError() from e
