import pytest

from . import helpers

class VerhoeffTest:
    def test_verhoeff_check_digit(self):
        assert helpers.verhoeff_digit('123456654321') == '9'
        assert helpers.verhoeff_digit('1') == '5'
        assert helpers.verhoeff_digit('11') == '3'
        assert helpers.verhoeff_digit(
            '5743839105748193475681981039847561718657489228374') == '3'
        assert helpers.verhoeff_digit('123456654321') == '9'
        assert helpers.verhoeff_digit('10003729') == '1'
        assert helpers.verhoeff_digit('505') == '3'
        assert helpers.verhoeff_digit('050') == '3'
        assert helpers.verhoeff_digit('161') == '8'
        assert helpers.verhoeff_digit('616') == '8'
        assert helpers.verhoeff_digit('272') == '5'
        assert helpers.verhoeff_digit('727') == '5'
        assert helpers.verhoeff_digit('494') == '1'
        assert helpers.verhoeff_digit('949') == '1'
        assert helpers.verhoeff_digit('383') == '4'
        assert helpers.verhoeff_digit('838') == '9'
        assert helpers.verhoeff_digit('505505') == '2'
        assert helpers.verhoeff_digit('050050') == '4'
