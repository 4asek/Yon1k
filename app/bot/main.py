import asyncio
from aiogram import Bot, Dispatcher
from app.config import TELEGRAM_TOKEN
from app.db.session import engine, SessionLocal
from app.db.models import Base

from app.bot.routers.basic import router as basic_router
from app.bot.routers.tasks import router as tasks_router
from app.bot.routers.rewards import router as rewards_router

async def on_startup():
    # Створюємо таблиці, якщо їх ще немає
    Base.metadata.create_all(bind=engine)

    # Перевіряємо підключення до БД
    try:
        with SessionLocal() as _:
            conn = engine.raw_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT @@SERVERNAME, DB_NAME()")
            server_name, db_name = cursor.fetchone()
            print(f"[DB] ✅ Підключено до сервера: {server_name}, база: {db_name}")
            conn.close()
    except Exception as e:
        print(f"[DB] ❌ Помилка підключення: {e}")
        raise

async def main():
    await on_startup()
    print("[BOT] ✅ Бот запущений і слухає команди...")
    bot = Bot(token=TELEGRAM_TOKEN)
    dp = Dispatcher()
    dp.include_router(basic_router)
    dp.include_router(tasks_router)
    dp.include_router(rewards_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
