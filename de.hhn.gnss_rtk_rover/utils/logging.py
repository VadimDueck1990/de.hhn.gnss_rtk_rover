"""
Logger class.

Simple logging class.

Created on 27 Sep 2022

:author: vdueck
"""

import sys

CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

_level_dict = {
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
}

_stream = sys.stderr


class Logger:
    """
    WiFiManager class.
    """

    level = NOTSET

    def __init__(self, name):
        """Constructor.

        :param str name: name of the calling class
        """
        self.name = name

    def _level_str(self, level):
        """
        returns the set log level

        :return: log level
        :rtype: _level_dict
        """
        l = _level_dict.get(level)
        if l is not None:
            return l
        return "LVL%s" % level

    def setLevel(self, level):
        """
        sets the log level

        :param _level_dict level: the wanted log level
        """
        self.level = level

    def log(self, level, msg, *args):
        """
        log a message to the console with the given log level

        :param _level_dict level: the wanted log level
        :param str msg: the log message
        :param args: optional payload
        """
        if level >= (self.level or _level):
            _stream.write("%s:%s:" % (self._level_str(level), self.name))
            if not args:
                print(msg, file=_stream)
            else:
                print(msg % args, file=_stream)

    def debug(self, msg, *args):
        """
        log a DEBUG message to the console

        :param str msg: the log message
        :param args: optional payload
        """
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        """
        log an INFO message to the console

        :param str msg: the log message
        :param args: optional payload
        """
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        """
        log an WARNING message to the console

        :param str msg: the log message
        :param args: optional payload
        """
        self.log(WARNING, msg, *args)

    warn = warning

    def error(self, msg, *args):
        """
        log an ERROR message to the console

        :param str msg: the log message
        :param args: optional payload
        """
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        """
        log an CRITICAL message to the console

        :param str msg: the log message
        :param args: optional payload
        """
        self.log(CRITICAL, msg, *args)

    def exc(self, e, msg, *args):
        """
        log an Exception message to the console

        :param str msg: the log message
        :param exception e: the thrown exception
        :param args: optional payload
        """
        self.log(ERROR, msg, *args)
        sys.print_exception(e, _stream)


_level = DEBUG
_loggers = {}


def getLogger(name) -> Logger:
    if name not in _loggers:
        _loggers[name] = Logger(name)
    return _loggers[name]

