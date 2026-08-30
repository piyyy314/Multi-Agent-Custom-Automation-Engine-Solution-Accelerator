import pytest
from common.config.app_config import config
from common.models.messages_af import UserLanguage


def test_set_user_local_browser_language_rejection():
    """Test that set_user_local_browser_language rejects invalid or malicious language strings (e.g. log injection/CRLF)."""
    original_lang = config.get_user_local_browser_language()
    try:
        # Malicious string with CRLF injection
        malicious_lang = "en-US\r\nCRITICAL LOG FORGERY ATTEMPT"
        config.set_user_local_browser_language(malicious_lang)

        # Ensure setting invalid language code was rejected and original/fallback retained
        assert config.get_user_local_browser_language() != malicious_lang

        # Valid language string
        valid_lang = "fr-FR"
        config.set_user_local_browser_language(valid_lang)
        assert config.get_user_local_browser_language() == valid_lang
    finally:
        config.set_user_local_browser_language(original_lang)


def test_user_browser_language_endpoint_sanitization(caplog):
    """Test that user_browser_language_endpoint sanitizes input before logging to prevent CRLF injection."""
    from unittest.mock import patch, MagicMock
    import asyncio

    caplog.set_level("INFO")
    # Bypass regex pattern validation using construct
    user_lang = UserLanguage.construct(language="en-US\r\nINJECTED_LOG_LINE")

    with patch("app.config") as mock_config:
        from app import user_browser_language_endpoint
        asyncio.run(user_browser_language_endpoint(user_lang, None))

    log_messages = [record.getMessage() for record in caplog.records if record.name == "root"]
    target_log = [msg for msg in log_messages if "Received browser language" in msg][0]

    assert "\r" not in target_log
    assert "\n" not in target_log
    assert "en-USINJECTED_LOG_LINE" in target_log
