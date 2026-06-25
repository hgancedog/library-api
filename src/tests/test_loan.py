from datetime import date, timedelta

from app.models import Loan


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
