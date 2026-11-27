"""Три сценария формы бронирования: успех, отказ и найденный дефект."""

from datetime import date, timedelta

import pytest
from playwright.sync_api import expect

from pages.booking_page import BookingPage


@pytest.fixture
def booking_page(page, base_url) -> BookingPage:
    booking = BookingPage(page, base_url)
    booking.open()
    return booking


def _booking(**overrides) -> dict:
    """Заявка, которая проходит все реализованные проверки формы."""
    data = {
        "room": "medium",
        "date": (date.today() + timedelta(days=7)).isoformat(),
        "start_time": "10:00",
        "end_time": "11:00",
        "participants": "4",
        "name": "Анна Смирнова",
        "email": "anna.smirnova@company.ru",
    }
    data.update(overrides)
    return data


def test_successful_booking(booking_page: BookingPage):
    """Корректная заявка показывает комнату, дату, время и имя заявителя."""
    data = _booking()

    booking_page.fill_form(**data)
    booking_page.submit()

    expect(booking_page.status).to_contain_text(booking_page.SUCCESS_TITLE)
    expect(booking_page.status).to_contain_text(
        booking_page.success_details(
            room=data["room"],
            date=data["date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            name=data["name"],
        )
    )


def test_invalid_booking(booking_page: BookingPage):
    """Почта без корректного формата не создаёт бронь."""
    booking_page.fill_form(**_booking(email="anna.company.ru"))
    booking_page.submit()

    expect(booking_page.email_error).to_have_text(booking_page.EMAIL_FORMAT_ERROR)
    expect(booking_page.status).to_have_text(booking_page.VALIDATION_SUMMARY)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "BUG-01: форма создаёт бронь на 15 минут, хотя длительность "
        "должна быть от 30 минут до 4 часов"
    ),
    raises=AssertionError,
)
def test_discovered_defect(booking_page: BookingPage):
    """Встреча короче 30 минут должна отклоняться, а не подтверждаться."""
    booking_page.fill_form(**_booking(start_time="10:00", end_time="10:15"))
    booking_page.submit()

    expect(booking_page.status).to_have_text(booking_page.VALIDATION_SUMMARY)
    expect(booking_page.end_time_error).not_to_be_empty()
