# coding=utf-8
"""Helpers and assorted utilities"""
import time


class Timer(object):
    """Context manager to time potentially slow code blocks ( development aid )"""

    def __enter__(self):
        self.start = time.clock()
        return self

    def __exit__(self, *args):
        self.end = time.clock()
        self.interval = self.end - self.start
