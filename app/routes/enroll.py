from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserResponse, UserCreateRequest
from app.controllers import user_controller

router = APIRouter()

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    create_user_request: UserCreateRequest,
    db: Session = Depends(get_db),
):
    return user_controller.create_user(create_user_request, db)