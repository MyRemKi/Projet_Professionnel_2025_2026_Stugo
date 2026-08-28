# Tests unitaires pour la classe ColorValue (domain/value_objects/color_value.py)

import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.value_objects.color_value import ColorValue


class TestColorValueConstruction(unittest.TestCase):

    def test_accepts_6_digit_hex_with_hash(self):
        c = ColorValue("#39d353")
        self.assertEqual(c.hex, "#39d353")

    def test_accepts_6_digit_hex_without_hash(self):
        c = ColorValue("39d353")
        self.assertEqual(c.hex, "39d353")

    def test_accepts_3_digit_hex(self):
        c = ColorValue("#fff")
        self.assertEqual(c.hex, "#fff")

    def test_rejects_invalid_length(self):
        with self.assertRaises(ValueError):
            ColorValue("#12345")

    def test_rejects_empty_string(self):
        with self.assertRaises(ValueError):
            ColorValue("")

    def test_is_immutable(self):
        c = ColorValue("#39d353")
        with self.assertRaises(FrozenInstanceError):
            c.hex = "#000000"


class TestColorValueTransforms(unittest.TestCase):

    def setUp(self):
        self.white = ColorValue("#ffffff")
        self.black = ColorValue("#000000")

    def test_darkened_returns_color_value(self):
        result = self.white.darkened(0.5)
        self.assertIsInstance(result, ColorValue)
        self.assertNotEqual(result.hex, self.white.hex)

    def test_lightened_returns_color_value(self):
        result = self.black.lightened(1.5)
        self.assertIsInstance(result, ColorValue)

    def test_hue_shifted_full_circle_is_noop(self):
        c = ColorValue("#39d353")
        shifted = c.hue_shifted(360)
        self.assertEqual(shifted.to_rgb(), c.to_rgb())

    def test_to_rgb_white(self):
        self.assertEqual(self.white.to_rgb(), (1.0, 1.0, 1.0))

    def test_to_rgb_black(self):
        self.assertEqual(self.black.to_rgb(), (0.0, 0.0, 0.0))

    def test_contrast_text_on_light_background(self):
        contrast = self.white.contrast_text()
        self.assertEqual(contrast.hex, "#1a1e23")

    def test_contrast_text_on_dark_background(self):
        contrast = self.black.contrast_text()
        self.assertEqual(contrast.hex, "#e8eef4")

    def test_str_returns_hex(self):
        self.assertEqual(str(self.white), "#ffffff")

    def test_from_rgb_roundtrip(self):
        c = ColorValue.from_rgb(1.0, 0.0, 0.0)
        self.assertEqual(c.hex, "#ff0000")


if __name__ == "__main__":
    unittest.main()
