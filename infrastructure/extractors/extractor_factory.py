# Choisit la bonne fonction de lecture (Excel ou CSV) selon l'extension du fichier

from infrastructure.extractors.excel_extractor import extract_all_sheets
from infrastructure.extractors.csv_extractor import extract_from_csv

class ExtractorFactory:
    HANDLERS = {
        ".xlsx": extract_all_sheets,
        ".xls": extract_all_sheets,
        ".csv": extract_from_csv,
    }

    @classmethod
    def get(cls, extension):
        ext = extension.lower()
        if ext not in cls.HANDLERS:
            raise ValueError(f"Format non supporte: {extension!r}")
        return cls.HANDLERS[ext]

    @classmethod
    def register(cls, extension, handler):
        cls.HANDLERS[extension.lower()] = handler

    @classmethod
    def supported(cls):
        return list(cls.HANDLERS.keys())
