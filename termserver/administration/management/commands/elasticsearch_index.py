# coding=utf-8
"""Index all concepts in the ElasticSearch index"""
__author__ = 'ngurenyaga'

from django.core.management.base import BaseCommand
from search.elasticsearch import bulk_index


class Command(BaseCommand):
    """Management command to bulk index concepts"""
    help = 'Carry out a bulk index - send all concepts to ElasticSearch'

    def handle(self, *args, **options):
        """The command's entry point"""
        bulk_index()

        self.stdout.write('Successfully indexed all Concepts')
