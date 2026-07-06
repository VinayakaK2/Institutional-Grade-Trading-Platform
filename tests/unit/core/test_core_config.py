from backend.core.config import AppSettings

def test_app_settings_defaults():
    settings = AppSettings()
    assert settings.env == "development"
    assert settings.debug is False
    assert settings.log_level == "INFO"
    assert settings.log_format == "json"

def test_app_settings_override(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("DEBUG", "True")
    settings = AppSettings()
    assert settings.env == "production"
    assert settings.debug is True
