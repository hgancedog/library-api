import pytest

from app.models import Email, User, UserError  # noqa: W291


def test_user_requires_username():
    with pytest.raises(UserError):
        User(username="", email=Email("johndoe@gmail.com"))


def test_user_created_with_valid_data():
    user = User("hector", Email("hector@gmail.com"))
    assert user.username == "hector"
    assert user.email.value == "hector@gmail.com"
