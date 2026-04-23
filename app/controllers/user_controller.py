from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.schemas.user import UserCreateRequest
from app.models.user import User


class UserController:
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.user_service = UserService(self.user_repository)
    
    def create_user(self, create_user_request: UserCreateRequest) -> User:
        return self.user_service.create_user(
            email=create_user_request.email,
            password=create_user_request.password,
            role=create_user_request.role,
            name=create_user_request.name
        )
