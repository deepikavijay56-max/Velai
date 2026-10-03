import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_sensitive_development_settings_are_disabled_by_default():
    settings = Settings(_env_file=None)

    assert settings.JWT_SECRET is None
    assert settings.ADMIN_INITIAL_CODE is None
    assert settings.DEV_MODE is False
    assert settings.DEV_OTP_CODE is None


def test_production_requires_a_jwt_secret():
    with pytest.raises(ValidationError, match="JWT_SECRET"):
        Settings(_env_file=None, ENVIRONMENT="production", JWT_SECRET=None)


def test_production_rejects_short_jwt_secrets():
    with pytest.raises(ValidationError, match="32 characters"):
        Settings(_env_file=None, ENVIRONMENT="production", JWT_SECRET="placeholder")
