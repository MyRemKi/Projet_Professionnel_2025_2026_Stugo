# Tests unitaires pour la classe ExtractorFactory (infrastructure/extractors/extractor_factory.py)

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.extractors.extractor_factory import ExtractorFactory
from infrastructure.extractors.excel_extractor import extract_all_sheets
from infrastructure.extractors.csv_extractor import extract_from_csv


class TestExtractorFactory(unittest.TestCase):

    def setUp(self):
        # Sauvegarde/restaure l'etat partage (dict de classe) pour ne pas polluer les autres tests.
        self._original_handlers = dict(ExtractorFactory.HANDLERS)

    def tearDown(self):
        ExtractorFactory.HANDLERS = self._original_handlers

    def test_get_returns_excel_handler_for_xlsx(self):
        self.assertIs(ExtractorFactory.get(".xlsx"), extract_all_sheets)

    def test_get_returns_excel_handler_for_xls(self):
        self.assertIs(ExtractorFactory.get(".xls"), extract_all_sheets)

    def test_get_returns_csv_handler_for_csv(self):
        self.assertIs(ExtractorFactory.get(".csv"), extract_from_csv)

    def test_get_is_case_insensitive(self):
        self.assertIs(ExtractorFactory.get(".CSV"), extract_from_csv)
        self.assertIs(ExtractorFactory.get(".XLSX"), extract_all_sheets)

    def test_get_raises_for_unsupported_extension(self):
        with self.assertRaises(ValueError):
            ExtractorFactory.get(".pdf")

    def test_register_adds_new_handler(self):
        custom_handler = lambda *args, **kwargs: None
        ExtractorFactory.register(".json", custom_handler)
        self.assertIs(ExtractorFactory.get(".json"), custom_handler)

    def test_register_is_case_insensitive(self):
        custom_handler = lambda *args, **kwargs: None
        ExtractorFactory.register(".JSON", custom_handler)
        self.assertIs(ExtractorFactory.get(".json"), custom_handler)

    def test_supported_lists_all_registered_extensions(self):
        supported = ExtractorFactory.supported()
        self.assertIn(".xlsx", supported)
        self.assertIn(".xls", supported)
        self.assertIn(".csv", supported)


if __name__ == "__main__":
    unittest.main()
