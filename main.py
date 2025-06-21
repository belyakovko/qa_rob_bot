import logging
import asyncio
import sys
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

async def close_bot_session(bot: Bot):
    """Корректное закрытие сессии бота"""
    try:
        if hasattr(bot, 'session'):
            await bot.session.close()
    except Exception as e:
        logger.warning(f"Ошибка при закрытии сессии: {e}")

async def main():
    bot = None
    try:
        # Инициализация бота
        bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
        dp = Dispatcher(storage=MemoryStorage())
        
        # Регистрация обработчиков
        logger.info("=== Инициализация бота ===")
        router = CommandRouter(dp)
        router.register_handlers()

        # Пропуск накопившихся сообщений (альтернатива skip_updates)
        await bot.delete_webhook(drop_pending_updates=True)

        logger.info("=== Запуск бота ===")
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
            close_bot_session=True,
            timeout=30,
            relax=0.1
        )
        
    except asyncio.CancelledError:
        logger.info("Получен сигнал завершения работы")
    except Exception as e:
        logger.critical(f"Фатальная ошибка: {e}", exc_info=True)
        raise
    finally:
        logger.info("Завершение работы бота...")
        if bot:
            await close_bot_session(bot)
        logger.info("Бот остановлен")

def run_bot():
    if sys.platform == 'win32':
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
        logger.critical(f"Неожиданная ошибка: {e}", exc_info=True)
    finally:
        tasks = asyncio.all_tasks(loop=loop)
        for t in tasks:
            t.cancel()
        if tasks:
            loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))
        loop.close()
        logger.info("Event loop закрыт")

if __name__ == "__main__":
    run_bot()
