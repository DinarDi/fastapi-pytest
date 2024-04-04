from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import UserResponse, UserCreate, ApiUserResponse, ApiUserListResponse
from database import db_manager
from api_v1.users import crud as users_crud


router = APIRouter(
    tags=['Users']
)


@router.post('/', response_model=ApiUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        payload: UserCreate,
        session: AsyncSession = Depends(db_manager.get_session),
):
    """View for create user"""
    user = await users_crud.create_user(
        session=session,
        payload=payload,
    )
    response = UserResponse.model_validate(user).model_dump()
    return JSONResponse(
        content={
            'data': response,
        },
        status_code=status.HTTP_201_CREATED,
    )


@router.get('/', response_model=ApiUserListResponse, status_code=status.HTTP_200_OK)
async def get_users(session: AsyncSession = Depends(db_manager.get_session)):
    """View for get users"""
    users = await users_crud.get_users(session=session)
    response = [
        UserResponse.model_validate(user).model_dump() for user in users
    ]
    return JSONResponse(
        content={
            'data': response,
        },
        status_code=status.HTTP_200_OK,
    )
