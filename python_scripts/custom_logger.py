#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding: utf8
import logging
from ffxiv_aku import *


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    FORMATS = {
        logging.DEBUG: wrap_in_color_green(format),
        logging.INFO: wrap_in_color_blue(format),
        logging.WARNING: wrap_in_color_yellow(format),
        logging.ERROR: wrap_in_color_red(format),
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def getLogger():
    logger = logging.getLogger("My_app")
    logger.setLevel(logging.CRITICAL)
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    return logger
