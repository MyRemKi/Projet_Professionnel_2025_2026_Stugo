# Fonctions simples pour lire/ecrire la session et les preferences (utilisees par settings_page)

from infrastructure.persistence.session_repository import SessionRepository
from infrastructure.persistence.preferences_repository import PreferencesRepository

def sr(): return SessionRepository.instance()
def pr(): return PreferencesRepository.instance()

def load_session() -> dict: return sr().load_session()
def save_session(data: dict) -> bool: return sr().save_session(data)
def clear_session() -> bool: return sr().clear_session()
def load_prefs() -> dict: return pr().load()
def save_prefs(data: dict) -> bool: return pr().save(data)
def get_session_dir() -> str: return sr().get_session_dir()
