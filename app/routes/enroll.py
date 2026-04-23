from fastapi import APIRouter, Depends, status
from app.schemas.user import UserResponse, UserCreateRequest
from app.controllers.user_controller import UserController
from app.core.container import get_user_controller

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    create_user_request: UserCreateRequest,
    user_controller: UserController = Depends(get_user_controller),
):
    return user_controller.create_user(create_user_request)