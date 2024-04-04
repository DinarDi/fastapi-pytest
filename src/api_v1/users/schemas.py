from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    username: str
    email: str


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    pass


class UserResponse(UserBase):
    """Схема пользователя"""
    id: int
    model_config = ConfigDict(from_attributes=True)


class ApiUserBase(BaseModel):
    """Базовая схема ответа на запрос пользователя"""
    pass


class ApiUserResponse(ApiUserBase):
    """Схема ответа на запрос одного пользователя"""
    data: UserResponse


class ApiUserListResponse(ApiUserBase):
    """Схема ответа на запрос пользователей"""
    data: list[UserResponse]
