import logging

from app.core.settings import settings


class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt, datefmt):
        super().__init__()
        self.fmt = fmt
        self.datefmt = datefmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset,
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt, datefmt=self.datefmt)
        return formatter.format(record)


def get_logger(name: str | None = None):
    # create logger
    logger = logging.getLogger(name)

    logger.setLevel(logging.DEBUG if settings.LOG_LEVEL == "DEBUG" else logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if settings.LOG_LEVEL == "DEBUG" else logging.INFO)

    # add formatter to ch
    ch.setFormatter(
        CustomFormatter(
            fmt="%(levelname)s | %(asctime)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    # add ch to logger
    logger.addHandler(ch)

    return logger


logger = get_logger(name="app")
