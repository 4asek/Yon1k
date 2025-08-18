from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.db.session import SessionLocal
from app.db.crud import get_or_create_user, list_rewards, buy_reward

router = Router(name="rewards")

@router.message(Command("rewards"))
async def cmd_rewards(message: Message):
    with SessionLocal() as db:
        get_or_create_user(db, message.from_user.id, message.from_user.username)
        rewards = list_rewards(db)
    if not rewards:
        return await message.answer("Нагород поки немає.")
    lines = [f"#{r.RewardId} {r.Title} — {r.CostPoints} балів" for r in rewards]
    await message.answer("\n".join(lines) + "\nКупити: /buy ID")

@router.message(Command("buy"))
async def cmd_buy(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        return await message.answer("Формат: /buy ID")
    try:
        reward_id = int(parts[1])
    except ValueError:
        return await message.answer("ID має бути числом.")

    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id, message.from_user.username)
        ok, msg = buy_reward(db, user.UserId, reward_id)
    await message.answer(msg)
