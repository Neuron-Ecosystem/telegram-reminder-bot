# dispatcher.py

import asyncio
from datetime import datetime
from config import DISPATCH_INTERVAL 
from db_manager import DbManager
from base import BaseGateway # Нужен для типизации

class Dispatcher:
    # ИСПРАВЛЕНИЕ: Конструктор теперь принимает 3 аргумента (self, db_manager, gateways)
    def __init__(self, db_manager: DbManager, gateways: list[BaseGateway]): 
        self.db_manager = db_manager
        self.gateways = gateways # Сохраняем список всех шлюзов (Telegram, VK и т.д.)
        self.is_running = True

    async def start(self):
        """Основной цикл диспетчера, который проверяет напоминания."""
        print("Dispatcher запущен и готов к работе.")
        
        while self.is_running:
            try:
                # 1. Получаем список напоминаний, срок которых наступил
                due_reminders = self.db_manager.get_due_reminders()
                
                if due_reminders:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Найдено {len(due_reminders)} напоминаний для отправки.")
                
                # 2. Обрабатываем каждое напоминание
                for reminder in due_reminders:
                    # 3. Находим соответствующий шлюз (Telegram, VK)
                    gateway = self._get_gateway(reminder.platform)
                    
                    if gateway:
                        # 4. Формируем и отправляем сообщение
                        message = f"🔔 **НАПОМИНАНИЕ!**\n\n{reminder.text}"
                        await gateway.send_message(reminder.user_id, message)
                        
                        # 5. Помечаем как отправленное в БД
                        self.db_manager.mark_as_sent(reminder.id)
                    else:
                        print(f"Ошибка: Не найден шлюз для платформы '{reminder.platform}'")

            except Exception as e:
                # Критическая ошибка в цикле, но продолжаем работу
                print(f"Критическая ошибка в цикле диспетчера: {e}")

            # Ожидание перед следующей проверкой
            await asyncio.sleep(DISPATCH_INTERVAL)
            
        print("Dispatcher остановлен.")

    def stop(self):
        """Останавливает цикл диспетчера."""
        self.is_running = False

    def _get_gateway(self, platform_name: str) -> BaseGateway | None:
        """Находит шлюз по имени платформы."""
        for gateway in self.gateways:
            if gateway.platform == platform_name:
                return gateway
        return None
