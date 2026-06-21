import pytest

from app.models import Email


def test_email_rejects_invalid_format():
    with pytest.raises(ValueError):
        Email("without_sign")


def test_email_normalizes_to_lowercase():
    email = Email("User@Example.com")
    assert email.value == "user@example.com"
