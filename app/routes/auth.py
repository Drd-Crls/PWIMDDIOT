from fastapi import APIRouter, Depends, status
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.controllers.auth_controller import AuthController
from app.core.dependencies import get_current_user
from app.core.container import get_auth_controller

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    login_request: LoginRequest,
    auth_controller: AuthController = Depends(get_auth_controller),
):
    return auth_controller.login(login_request)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user),
):
    return current_user