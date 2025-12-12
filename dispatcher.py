# dispatcher.py (Был core/dispatcher.py)

import asyncio
from datetime import datetime
from config import DISPATCH_INTERVAL
from db_manager import DbManager  # Изменение: импорт из db_manager
from base import BaseGateway  # Изменение: импорт из base


class Dispatcher:
    """Асинхронный цикл, который постоянно проверяет БД на наличие напоминаний к отправке."""

    def __init__(self, gateways: dict[str, BaseGateway]):
        self.db_manager = DbManager()
        self.gateways = gateways

    async def _send_reminder_task(self, reminder):
        """Задача по отправке одного напоминания."""
        platform = reminder.platform
        gateway = self.gateways.get(platform)

        if gateway:
            try:
                message = f"🔔 **НАПОМИНАНИЕ!**\n\n{reminder.text}"
                await gateway.send_message(reminder.user_id, message)
                self.db_manager.mark_sent(reminder.id)
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Отправлено напоминание {reminder.id} на {platform}."
                )
            except Exception as e:
                self.db_manager.mark_sent(reminder.id)
                print(
                    f"Ошибка отправки/пользователь недоступен {reminder.id} на {platform}: {e}"
                )
        else:
            print(f"Неизвестная платформа: {platform} для напоминания {reminder.id}")

    async def run_dispatcher(self):
        """Главный асинхронный цикл проверки."""
        print(f"Диспетчер запущен, интервал проверки: {DISPATCH_INTERVAL} сек.")
        while True:
            try:
                due_reminders = self.db_manager.get_due_reminders()

                if due_reminders:
                    tasks = [self._send_reminder_task(r) for r in due_reminders]
                    await asyncio.gather(*tasks)

            except Exception as e:
                print(f"Критическая ошибка в диспетчере: {e}")

            await asyncio.sleep(DISPATCH_INTERVAL)
