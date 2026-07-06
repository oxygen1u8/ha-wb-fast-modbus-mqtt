import logging
import sys


class ModbusLogger(logging.Logger):
    DEFAULT_FORMAT = "[%(asctime)s][%(levelname)s]%(message)s"
    DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

    class PrefixFilter(logging.Filter):
        def filter(self, record):
            if isinstance(record.msg, str):
                record.msg = f"[{record.name}]:{record.msg}"
            return True

    def __init__(self, name: str, level=logging.NOTSET) -> None:
        super().__init__(name, level)
        self._setup_default_handler()

    def _setup_default_handler(self):
        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter(self.DEFAULT_FORMAT, datefmt=self.DEFAULT_DATEFMT)
        handler.setFormatter(formatter)
        handler.addFilter(self.PrefixFilter())

        self.addHandler(handler)
        self.propagate = False


logging.setLoggerClass(ModbusLogger)


def get_logger(name: str):
    return logging.getLogger(name)
