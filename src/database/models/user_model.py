from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """Модель пользователя"""
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
