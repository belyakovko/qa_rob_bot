import logging
import asyncio
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers import CommandRouter

from aiogram import Dispatcher

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
    bot = Bot(
        token=Config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher(storage=MemoryStorage())

    try:
        logger.info("=== Инициализация бота ===")
        router = CommandRouter(dp)
        router.register_handlers()

        logger.info("=== Запуск бота ===")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except asyncio.CancelledError:
        logger.info("Получен сигнал завершения работы")
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}", exc_info=True)
    finally:
        logger.info("Завершение работы бота...")
        await bot.session.close()
        logger.info("Бот остановлен")

def run_bot():
    if sys.platform == 'win32':
        # На Windows используем SelectorEventLoop вместо Proactor
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        task = loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")
        task.cancel()
        loop.run_until_complete(task)
    except Exception as e:
        logger.critical(f"Неожиданная ошибка: {e}")
    finally:
        # Даем время на завершение всех задач
        tasks = asyncio.all_tasks(loop=loop)
        for t in tasks:
            t.cancel()
        if tasks:
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()
        logger.info("Event loop закрыт")

if __name__ == "__main__":
    run_bot()