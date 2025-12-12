# telegram.py

from base import BaseGateway
from db_manager import DbManager
from config import TELEGRAM_TOKEN
from aiogram import Bot, Dispatcher as AioDispatcher, types
# Используем более стабильный импорт для DefaultBotProperties (мы это исправляли ранее)
from aiogram.client.bot import DefaultBotProperties 
from aiogram.enums import ParseMode
from aiogram.filters import Command
import asyncio


class TelegramGateway(BaseGateway):
    """Реализация шлюза для Telegram с использованием aiogram."""

    def __init__(self, db_manager: DbManager):
        super().__init__("telegram")
        self.db_manager = db_manager

        # Инициализация с использованием DefaultBotProperties
        default_properties = DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
        self.bot = Bot(token=TELEGRAM_TOKEN, defaults=default_properties)

        self.dp = AioDispatcher()

        # Регистрация обработчиков
        self.dp.message.register(self.handle_start, Command("start"))
        self.dp.message.register(self.handle_remind, Command("remind"))
        self.dp.message.register(self.handle_list, Command("list"))
        self.dp.message.register(self.handle_clear, Command("clear"))

    async def send_message(self, user_id: str, text: str):
        """Отправляет сообщение пользователю Telegram."""
        # aiogram может работать с int, но везде мы используем str для единообразия
        await self.bot.send_message(int(user_id), text)

    async def handle_start(self, message: types.Message):
        """Обработка команды /start (инструкция)."""
        help_text = (
            "Привет! Я твой кроссплатформенный бот-планировщик.\n\n"
            "**Как добавить напоминание?**\n"
            "Напиши `/remind <время> <текст>`.\n\n"
            "*Примеры:*\n"
            "`/remind через 1 час купить молоко`\n"
            "`/remind 11:30 созвон`\n\n"
            "**Полезные команды:**\n"
            "`/list` — показать активные напоминания.\n"
            "`/clear` — удалить все активные напоминания."
        )
        await message.answer(help_text)

    async def handle_remind(self, message: types.Message):
        """Обработка команды /remind (создание напоминания)."""
        
        # ИСПРАВЛЕНИЕ ПАРСИНГА: Надежно отделяем команду от текста
        parts = message.text.split(maxsplit=1) 
        
        if len(parts) < 2:
            await message.answer("Пожалуйста, укажите время и текст напоминания.")
            return

        raw_text = parts[1].strip() # Это 'время текст'

        user_id = str(message.from_user.id)
        
        # ПОРЯДОК: Передаем аргументы в порядке (platform, user_id, raw_text)
        response = self.db_manager.add_reminder(self.platform, user_id, raw_text)
        await message.answer(response)

    async def handle_list(self, message: types.Message):
        """Обработка команды /list (просмотр активных напоминаний)."""
        user_id = str(message.from_user.id)
        
        # Имя метода изменено на get_active_reminders для совместимости с db_manager.py
        reminders = self.db_manager.get_active_reminders(user_id, self.platform)

        if not reminders:
            await message.answer("Пусто! 🎉 У вас нет активных напоминаний.")
            return

        list_text = "📝 **Ваши активные напоминания:**\n"
        for i, r in enumerate(reminders, 1):
            list_text += f"{i}. `{r.due_date.strftime('%H:%M %d-%m')}` — {r.text}\n"

        await message.answer(list_text)

    async def handle_clear(self, message: types.Message):
        """Обработка команды /clear (удаление всех напоминаний)."""
        user_id = str(message.from_user.id)
        
        # Имя метода изменено на clear_all_reminders для совместимости с db_manager.py
        count = self.db_manager.clear_all_reminders(user_id, self.platform)

        if count > 0:
            await message.answer(f"🗑️ Все {count} ваших активных напоминаний удалены.")
        else:
            await message.answer("Нечего удалять. Список напоминаний уже пуст.")

    async def run(self):
        """Запуск прослушивания Telegram Long Polling."""
        print("Telegram Gateway запущен.")
        await self.dp.start_polling(self.bot)
