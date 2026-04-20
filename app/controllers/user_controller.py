from fastapi import APIRouter, Depends, status
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.user_service import UserService
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    create_user_request: UserCreateRequest,
    db: Session = Depends(get_db),
):
    user_repository = UserRepository(db)
    user_service = UserService(user_repository)
    return user_service.create_user(
        email=create_user_request.email,
        password=create_user_request.password,
        role=create_user_request.role,
        name=create_user_request.name
    )
