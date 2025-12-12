# db_manager.py (Финально исправленная версия для dateparser 1.2.x)

import dateparser
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import datetime
from models import Reminder, SessionLocal


class DbManager:
    """Центральный класс для управления напоминаниями и парсинга времени."""

    def __init__(self):
        self.Session = SessionLocal

    def get_session(self) -> Session:
        return self.Session()

    def add_reminder(self, platform: str, user_id: str, raw_text: str) -> str:
        """Парсит текст, извлекает время и сохраняет напоминание."""

        parsed_date = dateparser.parse(
            raw_text,
            # ИЗМЕНЕНИЕ: LOCALES (LANGUAGES) вынесены из словаря settings
            languages=["ru", "en"],
            settings={"PREFER_DATES_FROM": "future"},
        )

        if not parsed_date or parsed_date < datetime.now():
            return "❌ Не удалось распознать **будущую** дату/время. Попробуйте так: `/remind 17:00 встреча`"

        with self.get_session() as session:
            reminder_text = raw_text.strip()

            new_reminder = Reminder(
                user_id=user_id,
                platform=platform,
                text=reminder_text,
                due_date=parsed_date,
            )
            session.add(new_reminder)
            session.commit()
            return f"✅ Напоминание сохранено! Я напомню о **'{new_reminder.text}'** в `{parsed_date.strftime('%H:%M %d-%m-%Y')}`."

    def get_due_reminders(self) -> list[Reminder]:
        """Получает напоминания, срок которых уже наступил, но которые еще не отправлены."""
        now = datetime.now()
        with self.get_session() as session:
            stmt = select(Reminder).where(
                Reminder.due_date <= now, Reminder.is_sent == False
            )
            return list(session.scalars(stmt).all())

    def mark_sent(self, reminder_id: int):
        """Отмечает напоминание как отправленное."""
        with self.get_session() as session:
            reminder = session.get(Reminder, reminder_id)
            if reminder:
                reminder.is_sent = True
                session.commit()

    def get_active_reminders(self, user_id: str, platform: str) -> list[Reminder]:
        """Получает список активных напоминаний для пользователя."""
        with self.get_session() as session:
            stmt = (
                select(Reminder)
                .where(
                    Reminder.user_id == user_id,
                    Reminder.platform == platform,
                    Reminder.is_sent == False,
                )
                .order_by(Reminder.due_date)
            )
            return list(session.scalars(stmt).all())

    def clear_all_reminders(self, user_id: str, platform: str):
        """Удаляет все активные напоминания пользователя."""
        with self.get_session() as session:
            stmt = delete(Reminder).where(
                Reminder.user_id == user_id,
                Reminder.platform == platform,
                Reminder.is_sent == False,
            )
            result = session.execute(stmt)
            session.commit()
            return result.rowcount
