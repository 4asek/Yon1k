from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.db.models import User, Task, Reward, UserReward, TaskEvent

#Users 
def get_or_create_user(db: Session, tg_id: int, username: Optional[str]) -> User:
    user = db.execute(select(User).where(User.TelegramId == tg_id)).scalar_one_or_none()
    if not user:
        user = User(TelegramId=tg_id, Username=username or None)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

#Tasks
def create_task(db: Session, user_id: int, title: str, total: int, reward: int) -> Task:
    task = Task(UserId=user_id, Title=title, TotalCount=total, RewardPoints=reward)
    db.add(task); db.commit(); db.refresh(task)
    return task

def list_tasks(db: Session, user_id: int) -> List[Task]:
    return db.execute(select(Task).where(Task.UserId == user_id).order_by(Task.IsCompleted, Task.TaskId)).scalars().all()

def mark_done(db: Session, user_id: int, task_id: int) -> Tuple[Optional[Task], int]:
    task = db.get(Task, task_id)
    if not task or task.UserId != user_id or task.IsCompleted:
        return None, 0
    task.CurrentCount += 1
    added_points = task.RewardPoints
    # complete?
    if task.CurrentCount >= task.TotalCount:
        task.IsCompleted = True
    # points update
    user = db.get(User, user_id)
    user.Points += added_points
    # audit
    db.add(TaskEvent(TaskId=task.TaskId, UserId=user_id))
    db.commit(); db.refresh(task); db.refresh(user)
    return task, added_points

# --- Points / Rewards ---
def get_points(db: Session, user_id: int) -> int:
    return db.get(User, user_id).Points

def list_rewards(db: Session) -> List[Reward]:
    return db.execute(select(Reward).order_by(Reward.CostPoints)).scalars().all()

def buy_reward(db: Session, user_id: int, reward_id: int) -> Tuple[bool, str]:
    reward = db.get(Reward, reward_id)
    user = db.get(User, user_id)
    if not reward:
        return False, "Нагороду не знайдено."
    if user.Points < reward.CostPoints:
        return False, f"Недостатньо балів. Потрібно {reward.CostPoints}, у тебе {user.Points}."
    user.Points -= reward.CostPoints
    db.add(UserReward(UserId=user_id, RewardId=reward_id))
    db.commit()
    return True, f"Куплено: {reward.Title} за {reward.CostPoints} балів."

# --- Seed (приклади нагород) ---
def seed_rewards_if_empty(db: Session) -> None:
    count = db.execute(select(func.count(Reward.RewardId))).scalar_one()
    if count == 0:
        db.add_all([
            Reward(Title="1 день прогулу (без докорів сумління)", CostPoints=100),
            Reward(Title="Смачний десерт", CostPoints=60),
            Reward(Title="1 серія улюбленого серіалу", CostPoints=40),
        ])
        db.commit()
