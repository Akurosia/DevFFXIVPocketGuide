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
    format = "%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d [%(filename)s > %(funcName)s])"
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


def getLogger(level=50):
    logger = logging.getLogger("My_app")
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    return logger


if __name__ == "__main__":
    #print(logging.DEBUG)    #10
    #print(logging.INFO)     #20
    #print(logging.WARNING)  #30
    #print(logging.ERROR)    #40
    #print(logging.CRITICAL) #50
    logger = getLogger(10)
    logger.debug("hi")
