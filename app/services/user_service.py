from app.models.user import User
from app.interfaces.repositories import UserRepositoryInterface
from app.core.security import hash_password
from app.interfaces.services import UserServiceInterface


class UserService(UserServiceInterface):
     
    def __init__(self, user_repository: UserRepositoryInterface):
        self.user_repository = user_repository
    
    def create_user(
        self, 
        email: str, 
        password: str, 
        role: str, 
        name: str
    ) -> User:
        password_hash = hash_password(password)
        new_user = User(
            email=email, 
            password=password_hash, 
            role=role, 
            name=name
        )
        return self.user_repository.create(new_user)
