"""Test configuration for the magpie package."""

import pytest


@pytest.fixture(autouse=True)
def mock_env_variables():
    """Mock environment variables needed for tests."""
    with pytest.MonkeyPatch().context() as mp:
        mp.setenv("HN_USER_COOKIE", "test_cookie_value")
        yield mp
