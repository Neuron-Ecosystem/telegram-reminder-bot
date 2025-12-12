# db_manager.py

from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Reminder, init_db # init_db нам нужен для создания таблиц
from dateparser import parse
import time # Используем time.sleep в Dispatcher

class DbManager:
    def __init__(self, db_url):
        # 1. Инициализируем движок и создаем таблицы, если они не существуют
        self.engine = init_db(db_url) 
        
        # 2. Создаем фабрику сессий, привязанную к движку
        self.Session = sessionmaker(bind=self.engine)

    # --- CRUD ОПЕРАЦИИ ---

    def add_reminder(self, user_id, platform, text_body):
        # 1. Извлекаем команду и текст
        parts = text_body.split(maxsplit=1)
        if len(parts) < 2:
            return None, "Пожалуйста, укажите время и текст напоминания."
        
        time_str = parts[0]
        reminder_text = parts[1]
        
        # 2. Парсинг времени с учетом текущего времени (для относительных дат)
        # Настройка: prefer_dates_from='future' и настройки для русского языка (если langdetect установился)
        dt = parse(time_str, settings={'PREFER_DATES_FROM': 'future', 'LANGUAGES': ['ru', 'en']})
        
        if not dt:
            return None, "Не удалось распознать **будущую** дату/время. Попробуйте так: `/remind в 17:00 встреча`"

        # Убедимся, что дата в будущем
        if dt <= datetime.now():
            # Если дата в прошлом, пытаемся сдвинуть на следующий день, 
            # но только если это абсолютное время (например, '20:00')
            if ':' in time_str:
                 dt = dt.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
                 if dt <= datetime.now():
                    dt += timedelta(days=1)
            else:
                 return None, "Дата находится в прошлом. Укажите будущее время."


        # 3. Создаем объект напоминания
        new_reminder = Reminder(
            user_id=str(user_id),
            platform=platform,
            text=reminder_text,
            due_date=dt,
            is_sent=False
        )
        
        # 4. Сохраняем в БД
        session = self.Session()
        try:
            session.add(new_reminder)
            session.commit()
            return new_reminder, None
        except Exception as e:
            session.rollback()
            return None, f"Ошибка сохранения: {e}"
        finally:
            session.close()

    def get_due_reminders(self):
        session = self.Session()
        try:
            # SQLAlchemy 2.0: Используем .all() для получения списка
            now = datetime.now()
            reminders = session.query(Reminder).filter(
                Reminder.due_date <= now,
                Reminder.is_sent == False
            ).all()
            return reminders
        finally:
            session.close()

    def mark_as_sent(self, reminder_id):
        session = self.Session()
        try:
            # SQLAlchemy 2.0: Использование .one_or_none()
            reminder = session.query(Reminder).filter_by(id=reminder_id).one_or_none()
            if reminder:
                reminder.is_sent = True
                session.commit()
        finally:
            session.close()
            
    def get_user_reminders(self, user_id, platform):
        session = self.Session()
        try:
            # Получаем все неотправленные напоминания пользователя
            reminders = session.query(Reminder).filter(
                Reminder.user_id == str(user_id),
                Reminder.platform == platform,
                Reminder.is_sent == False
            ).order_by(Reminder.due_date).all()
            return reminders
        finally:
            session.close()

    def clear_user_reminders(self, user_id, platform):
        session = self.Session()
        try:
            deleted_count = session.query(Reminder).filter(
                Reminder.user_id == str(user_id),
                Reminder.platform == platform,
                Reminder.is_sent == False
            ).delete(synchronize_session='fetch')
            session.commit()
            return deleted_count
        finally:
            session.close()
