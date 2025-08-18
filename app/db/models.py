from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, BigInteger, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    UserId = Column(Integer, primary_key=True, autoincrement=True)
    TelegramId = Column(BigInteger, unique=True, index=True, nullable=False)
    Username = Column(String(255), nullable=True)
    Points = Column(Integer, nullable=False, default=0)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    Tasks = relationship("Task", back_populates="User", cascade="all, delete-orphan")
    Purchases = relationship("UserReward", back_populates="User", cascade="all, delete-orphan")

class Task(Base):
    __tablename__ = "Tasks"
    TaskId = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("Users.UserId"), nullable=False, index=True)
    Title = Column(String(255), nullable=False)
    TotalCount = Column(Integer, nullable=False)
    RewardPoints = Column(Integer, nullable=False, default=1)
    CurrentCount = Column(Integer, nullable=False, default=0)
    IsCompleted = Column(Boolean, nullable=False, default=False)
    CreatedAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    User = relationship("User", back_populates="Tasks")
    Events = relationship("TaskEvent", back_populates="Task", cascade="all, delete-orphan")

class TaskEvent(Base):
    __tablename__ = "TaskEvents"
    TaskEventId = Column(Integer, primary_key=True, autoincrement=True)
    TaskId = Column(Integer, ForeignKey("Tasks.TaskId"), nullable=False, index=True)
    UserId = Column(Integer, ForeignKey("Users.UserId"), nullable=False, index=True)
    HappenedAt = Column(DateTime, default=datetime.utcnow, nullable=False)

    Task = relationship("Task", back_populates="Events")

class Reward(Base):
    __tablename__ = "Rewards"
    RewardId = Column(Integer, primary_key=True, autoincrement=True)
    Title = Column(String(255), nullable=False)
    CostPoints = Column(Integer, nullable=False)

class UserReward(Base):
    __tablename__ = "UserRewards"
    UserRewardId = Column(Integer, primary_key=True, autoincrement=True)
    UserId = Column(Integer, ForeignKey("Users.UserId"), nullable=False, index=True)
    RewardId = Column(Integer, ForeignKey("Rewards.RewardId"), nullable=False, index=True)
    PurchaseDate = Column(DateTime, default=datetime.utcnow, nullable=False)

    User = relationship("User", back_populates="Purchases")
