"""Assorted utilities"""
# -coding=utf-8
from django.test import TestCase

from .helpers import verhoeff_digit


class VerhoeffTests(TestCase):

    def test_verhoeff_check_digit(self):
        self.assertEqual(verhoeff_digit('123456654321'), '9')
        self.assertEqual(verhoeff_digit('1'), '5')
        self.assertEqual(verhoeff_digit('11'), '3')
        self.assertEqual(verhoeff_digit('5743839105748193475681981039847561718657489228374'), '3')
        self.assertEqual(verhoeff_digit('123456654321'), '9')
        self.assertEqual(verhoeff_digit('10003729'), '1')
        self.assertEqual(verhoeff_digit('505'), '3')
        self.assertEqual(verhoeff_digit('050'), '3')
        self.assertEqual(verhoeff_digit('161'), '8')
        self.assertEqual(verhoeff_digit('616'), '8')
        self.assertEqual(verhoeff_digit('272'), '5')
        self.assertEqual(verhoeff_digit('727'), '5')
        self.assertEqual(verhoeff_digit('494'), '1')
        self.assertEqual(verhoeff_digit('949'), '1')
        self.assertEqual(verhoeff_digit('383'), '4')
        self.assertEqual(verhoeff_digit('838'), '9')
        self.assertEqual(verhoeff_digit('505505'), '2')
        self.assertEqual(verhoeff_digit('050050'), '4')
