# models.py

from sqlalchemy import create_engine, Column, Integer, Boolean, DateTime

# Важное изменение: импорт VARCHAR для лучшей совместимости с PostgreSQL
from sqlalchemy.dialects.postgresql import VARCHAR
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Определение базового класса
Base = declarative_base()


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True)
    # Используем VARCHAR вместо String для совместимости с PostgreSQL
    user_id = Column(VARCHAR(255), nullable=False)
    platform = Column(VARCHAR(50), nullable=False)
    text = Column(VARCHAR(500), nullable=False)
    due_date = Column(DateTime, nullable=False)
    is_sent = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Reminder(id={self.id}, user_id='{self.user_id}', due_date='{self.due_date}')>"


# Примечание: Функция init_db теперь будет принимать PostgreSQL URL
def init_db(db_url):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine
