from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.db.session import SessionLocal
from app.db.crud import get_or_create_user, get_points, seed_rewards_if_empty

router = Router(name="basic")

@router.message(Command("start"))
async def cmd_start(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id, message.from_user.username)
        seed_rewards_if_empty(db)

    await message.answer(
        "Привіт! Я трекер завдань з балами.\n\n"
        "📌 **Як працює система балів:**\n"
        "   - Складність 1 (легко) → 5 балів за раз\n"
        "   - Складність 2 (середньо) → 10 балів за раз\n"
        "   - Складність 3 (важко) → 15 балів за раз\n\n"
        "🛠 **Команди:**\n"
        "/addtask Назва;Повторів;Складність(1-3) — додати завдання\n"
        "/mytasks — список завдань\n"
        "/done ID — відмітити виконання\n"
        "/points — мої бали\n"
        "/rewards — нагороди\n"
        "/buy ID — купити нагороду"
    )


@router.message(Command("points"))
async def cmd_points(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id, message.from_user.username)
        pts = get_points(db, user.UserId)
    await message.answer(f"У тебе {pts} балів.")
