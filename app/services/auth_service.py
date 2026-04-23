from fastapi import HTTPException, status
from app.repositories.base_repository import UserRepositoryInterface
from app.services.token_service import TokenService
from app.core.security import verify_password
from app.schemas.auth import TokenResponse


class AuthService:
    
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
        self.token_service = TokenService()
    
    def login(self, email: str, password: str) -> TokenResponse:
        user = self.user_repository.get_by_email(email)
        
        if user is None or not verify_password(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        access_token = self.token_service.create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        
        return TokenResponse(access_token=access_token)
