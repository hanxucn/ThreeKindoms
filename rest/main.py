# -*- coding: utf-8 -*-
import logging
from logging import DEBUG, INFO, ERROR  # noqa: I101
from logging.handlers import RotatingFileHandler
import sys
import click  # noqa: I201


from rest.app import app


LOG_LEVEL_MAP = dict((logging.getLevelName(level), level) for level in (DEBUG, INFO, ERROR))  # noqa: C402
LOG_FORMAT = "%(asctime)s, %(levelname)s, %(filename)s:%(lineno)d, %(message)s"

LOG_COLLECTOR_LOGFILE = "/var/log/zbs/log_collector.INFO"


def setup_logger(log_file, log_level):
    formatter = logging.Formatter("[%(asctime)s: %(levelname)s/%(processName)s] %(message)s")
    handler = RotatingFileHandler(log_file, maxBytes=20000000, backupCount=1)  # default 20mb
    handler.setLevel(logging.getLevelName(log_level))
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.getLevelName(log_level))
    map(logger.removeHandler, logger.handlers)
    logger.addHandler(handler)


@click.command()
@click.option("--debug", default=False, is_flag=True, help="enable flask debug mode")
@click.option("--log-level", type=click.Choice(LOG_LEVEL_MAP.keys()), default="INFO")
@click.option("--log-file", default=LOG_COLLECTOR_LOGFILE)
def run_server(log_level, log_file, debug):
    level = LOG_LEVEL_MAP[log_level]
    setup_logger(log_file, level)
    app.run(host="0.0.0.0", debug=debug, port=10406)


if __name__ == "__main__":
    level = LOG_LEVEL_MAP["DEBUG"]
    logging.basicConfig(
        format=LOG_FORMAT, level=level, stream=sys.stdout,
    )
    app.run(host="0.0.0.0", port=10406)
