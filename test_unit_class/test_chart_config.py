# Tests unitaires pour la classe ChartConfig (domain/value_objects/chart_config.py)

import os
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.value_objects.chart_config import ChartConfig


class TestChartConfigDefaults(unittest.TestCase):

    def test_default_factory_matches_field_defaults(self):
        cfg = ChartConfig.default()
        self.assertEqual(cfg, ChartConfig())

    def test_default_values(self):
        cfg = ChartConfig.default()
        self.assertEqual(cfg.chart_type, "bar")
        self.assertEqual(cfg.x_col, "zone_label")
        self.assertEqual(cfg.y_col, "total_tco2")
        self.assertEqual(cfg.group_col, "aucun")
        self.assertEqual(cfg.top_n, 15)
        self.assertFalse(cfg.mode_3d)
        self.assertEqual(cfg.elev, 28)
        self.assertEqual(cfg.azim, -48)

    def test_is_immutable(self):
        cfg = ChartConfig.default()
        with self.assertRaises(FrozenInstanceError):
            cfg.chart_type = "pie"


class TestChartConfigTransforms(unittest.TestCase):

    def setUp(self):
        self.cfg = ChartConfig(chart_type="bar", x_col="a", y_col="b", group_col="c", top_n=5, mode_3d=False, elev=10, azim=20)

    def test_with_type_changes_only_chart_type(self):
        new_cfg = self.cfg.with_type("pie")
        self.assertEqual(new_cfg.chart_type, "pie")
        self.assertEqual(new_cfg.x_col, self.cfg.x_col)
        self.assertEqual(new_cfg.y_col, self.cfg.y_col)
        self.assertEqual(new_cfg.group_col, self.cfg.group_col)
        self.assertEqual(new_cfg.top_n, self.cfg.top_n)
        self.assertEqual(new_cfg.mode_3d, self.cfg.mode_3d)

    def test_with_type_does_not_mutate_original(self):
        self.cfg.with_type("pie")
        self.assertEqual(self.cfg.chart_type, "bar")

    def test_with_3d_sets_mode_and_angles(self):
        new_cfg = self.cfg.with_3d(elev=45, azim=90)
        self.assertTrue(new_cfg.mode_3d)
        self.assertEqual(new_cfg.elev, 45)
        self.assertEqual(new_cfg.azim, 90)
        self.assertEqual(new_cfg.chart_type, self.cfg.chart_type)

    def test_as_2d_disables_mode_3d_and_keeps_angles(self):
        cfg_3d = self.cfg.with_3d(elev=45, azim=90)
        cfg_2d = cfg_3d.as_2d()
        self.assertFalse(cfg_2d.mode_3d)
        self.assertEqual(cfg_2d.elev, 45)
        self.assertEqual(cfg_2d.azim, 90)

    def test_chained_transforms(self):
        result = self.cfg.with_type("scatter").with_3d(elev=1, azim=2).as_2d()
        self.assertEqual(result.chart_type, "scatter")
        self.assertFalse(result.mode_3d)
        self.assertEqual(result.elev, 1)
        self.assertEqual(result.azim, 2)


if __name__ == "__main__":
    unittest.main()
