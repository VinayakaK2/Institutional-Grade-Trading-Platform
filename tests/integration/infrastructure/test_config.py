from backend.infrastructure.config.manager import config_manager
from backend.infrastructure.config.settings import AppSettings

def test_app_settings_loading_and_defaults(monkeypatch):
    """Verifies that configuration correctly loads defaults and environment variables."""
    # Temporarily set environment variables
    monkeypatch.setenv("ENV", "staging")
    monkeypatch.setenv("DEBUG", "True")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    
    # We must clear the config manager cache so it reloads
    config_manager._configs.clear()
    
    settings = config_manager.load(AppSettings)
    
    assert settings.env == "staging"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"
    assert settings.secret_key == "test-secret"
    assert settings.project_name == "Swing Trade Bot" # Default fallback
