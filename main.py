# main.py

import asyncio
from db_manager import DbManager
from telegram import TelegramGateway
from dispatcher import Dispatcher
from config import TELEGRAM_TOKEN, DB_URL  # Удалили VK_TOKEN


async def main():
    # Проверяем, что токен Telegram установлен
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "ВАШ_ТОКЕН_ТЕЛЕГРАМ":
        print("Ошибка: Не указан токен Telegram в config.py.")
        return

    # 1. Инициализация менеджера БД (он использует DB_URL из config.py)
    db_manager = DbManager(DB_URL)

    # 2. Инициализация шлюза Telegram
    telegram_gateway = TelegramGateway(db_manager)
    gateways = [telegram_gateway]

    # 3. Инициализация диспетчера
    dispatcher = Dispatcher(db_manager, gateways)

    print("Запуск всех сервисов...")

    # 4. Запуск диспетчера и шлюза параллельно
    tasks = [
        asyncio.create_task(dispatcher.start()),
        *[asyncio.create_task(g.run()) for g in gateways],
    ]

    # Ожидание завершения всех задач (например, при Ctrl+C)
    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    print("Запуск бота-планировщика...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем.")
    except Exception as e:
        print(f"Произошла критическая ошибка: {e}")
