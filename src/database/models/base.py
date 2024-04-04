from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    declared_attr,
)


class Base(DeclarativeBase):
    """Base model"""
    __abstract__ = True

    @classmethod
    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Автоматическое создание названия таблицы"""
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(primary_key=True)
