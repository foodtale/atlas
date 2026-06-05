import pytest
from unittest.mock import patch

from django.test import override_settings

from atlas.services.otp_send_service import OTPSendService


@override_settings(DEBUG=True)
def test_debug_mode_logs_and_succeeds(caplog):
    import logging

    with caplog.at_level(logging.INFO, logger="atlas.services.otp_send_service"):
        result, error = OTPSendService.call(phone_number="9999999999", otp="123456")

    assert error is None
    assert result == {}


@override_settings(DEBUG=True)
def test_debug_mode_includes_phone_and_otp_in_log(caplog):
    import logging

    with caplog.at_level(logging.INFO, logger="atlas.services.otp_send_service"):
        OTPSendService.call(phone_number="9999999999", otp="123456")

    assert "9999999999" in caplog.text
    assert "123456" in caplog.text


@override_settings(DEBUG=False)
def test_production_mode_returns_error_without_gateway():
    result, error = OTPSendService.call(phone_number="9999999999", otp="123456")

    assert result is None
    assert error is not None
    assert error.message == "SMS gateway not configured."
