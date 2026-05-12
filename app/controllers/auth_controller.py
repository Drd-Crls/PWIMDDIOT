from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.interfaces.services import AuthServiceInterface
from app.interfaces.controllers import AuthControllerInterface
from app.schemas.auth import LoginRequest, TokenResponse


class AuthController(AuthControllerInterface):
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.auth_service: AuthServiceInterface = AuthService(self.user_repository)
    
    def login(self, login_request: LoginRequest) -> TokenResponse:
        return self.auth_service.login(
            login_request.email,
            login_request.password
        )
