"""
Testing Foundation (Phase 0)
Pytest configuration and global shared fixtures.
"""
import pytest
from typing import Generator
from unittest.mock import MagicMock

# --- Global Markers Configuration ---
# Pytest markers (e.g., @pytest.mark.unit, @pytest.mark.integration) are configured in pytest.ini

# --- Shared Fixtures ---

@pytest.fixture(scope="session")
def mock_logger() -> MagicMock:
    """Provides a mocked structlog logger for tests that require logging verification."""
    return MagicMock()

@pytest.fixture(scope="function")
def isolated_env(monkeypatch: pytest.MonkeyPatch) -> Generator[pytest.MonkeyPatch, None, None]:
    """
    Ensures that environment variables are strictly controlled during tests.
    By default, it clears all env vars to prevent local dev setups from passing tests.
    Tests should explicitly mock the env vars they need.
    """
    # Note: In a real scenario, you'd only clear specific prefixes or clear all and set bare minimums.
    # monkeypatch.delenv("DATABASE_URL", raising=False)
    yield monkeypatch

# --- Test Utilities ---
# Future test utilities for mocking DB, time (freezegun), etc., belong here.
