from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.db.session import SessionLocal
from app.db.crud import get_or_create_user, create_task, list_tasks, mark_done

router = Router(name="tasks")

# Стан машини
class AddTask(StatesGroup):
    waiting_for_title = State()
    waiting_for_total = State()
    waiting_for_difficulty = State()

@router.message(Command("addtask"))
async def cmd_addtask(message: Message, state: FSMContext):
    await state.set_state(AddTask.waiting_for_title)
    await message.answer("Введіть назву завдання:")

@router.message(AddTask.waiting_for_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(AddTask.waiting_for_total)
    await message.answer("Скільки разів потрібно виконати завдання?")

@router.message(AddTask.waiting_for_total)
async def process_total(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Введіть число!")
    await state.update_data(total=int(message.text))

    # Кнопки вибору складності
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Легко (5 балів)", callback_data="diff_1")],
            [InlineKeyboardButton(text="🟡 Середньо (10 балів)", callback_data="diff_2")],
            [InlineKeyboardButton(text="🔴 Важко (15 балів)", callback_data="diff_3")],
        ]
    )

    await state.set_state(AddTask.waiting_for_difficulty)
    await message.answer("Оберіть складність:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("diff_"))
async def process_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = int(callback.data.split("_")[1])
    points_map = {1: 5, 2: 10, 3: 15}
    reward = points_map[difficulty]

    data = await state.get_data()
    title = data["title"]
    total = data["total"]

    with SessionLocal() as db:
        user = get_or_create_user(db, callback.from_user.id, callback.from_user.username)
        task = create_task(db, user.UserId, title, total, reward)

    await state.clear()
    await callback.message.edit_text(
        f"✅ Додано завдання #{task.TaskId}: {task.Title} × {task.TotalCount} "
        f"(Складність: {difficulty}, +{task.RewardPoints} балів за раз)"
    )

# Список завдань
@router.message(Command("mytasks"))
async def cmd_mytasks(message: Message):
    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id, message.from_user.username)
        tasks = list_tasks(db, user.UserId)
    if not tasks:
        return await message.answer("Завдань поки немає. Додай через /addtask")
    lines = []
    for t in tasks:
        status = "✅" if t.IsCompleted else "⏳"
        lines.append(f"#{t.TaskId} {status} {t.Title} — {t.CurrentCount}/{t.TotalCount}, +{t.RewardPoints}/раз")
    await message.answer("\n".join(lines))

# Виконання завдання
@router.message(Command("done"))
async def cmd_done(message: Message):
    parts = message.text.strip().split()
    if len(parts) != 2:
        return await message.answer("Формат: /done ID")
    try:
        task_id = int(parts[1])
    except ValueError:
        return await message.answer("ID має бути числом.")

    with SessionLocal() as db:
        user = get_or_create_user(db, message.from_user.id, message.from_user.username)
        task, added = mark_done(db, user.UserId, task_id)
    if not task:
        return await message.answer("Завдання не знайдено або вже завершене.")
    suffix = " (завершено!)" if task.IsCompleted else ""
    await message.answer(f"Зараховано виконання '{task.Title}', +{added} балів{suffix}.")
