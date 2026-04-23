from dependency_injector import containers, providers
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.controllers.auth_controller import AuthController
from app.controllers.user_controller import UserController


class Container(containers.DeclarativeContainer):
    
    db = providers.Callable(SessionLocal)
    
    user_repository = providers.Factory(
        UserRepository,
        db=db
    )
    
    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository
    )
    
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository
    )
    
    auth_controller = providers.Factory(
        AuthController,
        db=db
    )
    
    user_controller = providers.Factory(
        UserController,
        db=db
    )


container = Container()


def get_auth_controller() -> AuthController:
    return container.auth_controller()


def get_user_controller() -> UserController:
    return container.user_controller()
