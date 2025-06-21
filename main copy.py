import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers import CommandRouter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("=== Инициализация бота ===")
        
        storage = MemoryStorage()
        bot = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode="HTML")
        )
        dp = Dispatcher(storage=storage)

        # Инициализация и регистрация обработчиков
        router = CommandRouter(dp)
        router.register_handlers()

        logger.info("=== Запуск бота ===")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
    finally:
        if 'bot' in locals():
            await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}", exc_info=True)