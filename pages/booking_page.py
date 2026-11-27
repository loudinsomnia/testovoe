"""Page Object одностраничной формы бронирования переговорной."""

from playwright.sync_api import Page, expect


class BookingPage:
    """Страница https://rcsi-science.github.io/demo-roomly/.

    Две колонки:
    - справочник слева: бренд, заголовок и вместимость комнат (только чтение);
    - форма «Детали встречи»: поля брони, тексты ошибок, статус и отправка.
    Данные никуда не уходят: отправка обрабатывается на странице.
    """

    ROOM_NAMES = {
        "small": "Малая",
        "medium": "Средняя",
        "large": "Большая",
    }

    SUCCESS_TITLE = "Бронирование создано."
    VALIDATION_SUMMARY = "Проверьте, пожалуйста, заполнение формы."
    EMAIL_FORMAT_ERROR = "Введите корректную рабочую почту."

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url

        self.page_title = page.get_by_role("heading", level=1)
        self.available_rooms = page.get_by_label("Доступные комнаты")

        self.form = page.locator("#booking-form")
        self.form_title = page.get_by_role("heading", name="Детали встречи")

        # Подписи полей содержат «*», поэтому совпадение по тексту нестрогое.
        self.room = page.get_by_label("Переговорная")
        self.date = page.get_by_label("Дата")
        self.start_time = page.get_by_label("Начало")
        self.end_time = page.get_by_label("Окончание")
        self.participants = page.get_by_label("Участники")
        self.applicant_name = page.get_by_label("Ваше имя")
        self.email = page.get_by_label("Рабочая почта")

        self.room_error = page.locator('[data-error-for="room"]')
        self.date_error = page.locator('[data-error-for="date"]')
        self.start_time_error = page.locator('[data-error-for="startTime"]')
        self.end_time_error = page.locator('[data-error-for="endTime"]')
        self.participants_error = page.locator('[data-error-for="participants"]')
        self.name_error = page.locator('[data-error-for="name"]')
        self.email_error = page.locator('[data-error-for="email"]')

        self.status = page.locator("#form-status")
        self.submit_button = page.get_by_role("button", name="Забронировать")

    def open(self) -> None:
        self.page.goto(self.base_url, wait_until="domcontentloaded")
        expect(self.form).to_be_visible()

    def fill_form(
        self,
        *,
        room: str,
        date: str,
        start_time: str,
        end_time: str,
        participants: str,
        name: str,
        email: str,
    ) -> None:
        self.room.select_option(room)
        self.date.fill(date)
        self.start_time.fill(start_time)
        self.end_time.fill(end_time)
        self.participants.fill(str(participants))
        self.applicant_name.fill(name)
        self.email.fill(email)

    def submit(self) -> None:
        self.submit_button.click()

    def success_details(
        self,
        *,
        room: str,
        date: str,
        start_time: str,
        end_time: str,
        name: str,
    ) -> str:
        """Строка подтверждения: комната, дата, интервал и имя заявителя."""
        room_name = self.ROOM_NAMES[room]
        return f"{room_name}, {date}, {start_time}–{end_time} · {name}"
