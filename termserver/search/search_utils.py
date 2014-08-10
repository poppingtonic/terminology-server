# coding=utf-8
"""Helpers and assorted utilities"""
from django.utils import timezone


class Timer(object):
    """Context manager to time potentially slow code blocks ( development aid )"""

    def __enter__(self):
        self.start = timezone.now()
        return self

    def __exit__(self, *args):
        self.end = timezone.now()
        self.delta = self.end - self.start
        self.interval = self.delta.total_seconds()
