from datetime import date, timedelta

import pytest

from app.models import Loan, LoanError


def test_loan_due_date_is_loan_date_plus_30_days():
    loan = Loan(book_id=1, user_id=1)
    assert loan.due_date == loan.loan_date + timedelta(days=30)


def test_loan_created_with_valid_data():
    loan = Loan(book_id=1, user_id=1)
    assert loan.book_id == 1
    assert loan.user_id == 1
    assert loan.loan_date == date.today()
    assert loan.return_date is None
    assert loan.loan_id is None


def test_loan_rejects_return_date_before_loan_date():
    with pytest.raises(LoanError, match="return_date cannot be earlier"):
        Loan(book_id=1, user_id=1, return_date=date.today() - timedelta(days=1))


def test_loan_is_active():
    loan = Loan(1, 1)
    assert loan.is_active() is True


def test_loan_is_not_active():
    loan = Loan(1, 1)
    loan.mark_as_returned()
    assert loan.is_active() is False
