import pytest
from oneorg.config import get_settings, Settings


@pytest.mark.asyncio
async def test_settings_defaults():
    settings = Settings()
    assert "sqlite" in settings.database_url
    assert settings.secret_key == "dev-secret-change-in-production"
    assert settings.access_token_expire_days == 7


@pytest.mark.asyncio
async def test_settings_from_env():
    import os
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["DATABASE_URL"] = "postgresql://test"
    
    settings = Settings()
    assert settings.secret_key == "test-secret-key"
    assert settings.database_url == "postgresql://test"
    
    # Cleanup
    del os.environ["SECRET_KEY"]
    del os.environ["DATABASE_URL"]
