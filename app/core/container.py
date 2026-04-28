from dependency_injector import containers, providers
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.context_repository import ContextRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.context_service import ContextService
from app.controllers.auth_controller import AuthController
from app.controllers.user_controller import UserController
from app.controllers.context_controller import ContextController


class Container(containers.DeclarativeContainer):
    
    db = providers.Callable(SessionLocal)
    
    user_repository = providers.Factory(
        UserRepository,
        db=db
    )

    context_repository = providers.Factory(
        ContextRepository,
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

    context_service = providers.Factory(
        ContextService,
        context_repository=context_repository
    )
    
    auth_controller = providers.Factory(
        AuthController,
        db=db
    )
    
    user_controller = providers.Factory(
        UserController,
        db=db
    )

    context_controller = providers.Factory(
        ContextController,
        db=db
    )


container = Container()


def get_auth_controller() -> AuthController:
    return container.auth_controller()


def get_user_controller() -> UserController:
    return container.user_controller()


def get_context_controller() -> ContextController:
    return container.context_controller()
