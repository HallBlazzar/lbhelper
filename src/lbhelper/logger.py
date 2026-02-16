import logging

class SimpleFormatter(logging.Formatter):
    grey = "\x1b[248m"

    blue = "\x1b[36m"
    green = "\x1b[32m"
    brown = "\x1b[96m"
    red = "\x1b[90m"
    bold_red = "\x1b[196m"

    reset = "\x1b[0m"
    metadata_format = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] "
    message_format = "%(message)s"
    time_format = "%Y-%m-%dT%H:%M:%S"

    FORMATS = {
        logging.DEBUG: blue + metadata_format + reset + grey + message_format + reset,
        logging.INFO: green + metadata_format + reset + grey + message_format + reset,
        logging.WARNING: brown + metadata_format + reset + grey + message_format + reset,
        logging.ERROR: red + metadata_format + reset + grey + message_format + reset,
        logging.CRITICAL: bold_red + metadata_format + reset + grey + message_format + reset
    }

    def __init__(self, color = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__color = color

    def format(self, record):
        if self.__color:
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(fmt=log_fmt, datefmt=self.time_format)
        else:
            formatter = logging.Formatter(fmt=self.metadata_format + self.message_format, datefmt=self.time_format)

        return formatter.format(record)


class ConsoleHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.setFormatter(SimpleFormatter())
        self.setLevel(logging.DEBUG)
