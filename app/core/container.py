from dependency_injector import containers, providers
from sqlalchemy.orm import Session
from app.settings.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.context_repository import ContextRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.sensor_repository import SensorRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.context_service import ContextService
from app.services.device_service import DeviceService
from app.services.sensor_service import SensorService
from app.controllers.auth_controller import AuthController
from app.controllers.user_controller import UserController
from app.controllers.context_controller import ContextController
from app.controllers.device_controller import DeviceController
from app.controllers.sensor_controller import SensorController
from app.interfaces.services import (
    AuthServiceInterface,
    UserServiceInterface,
    ContextServiceInterface,
    DeviceServiceInterface,
    SensorServiceInterface,
)
from app.interfaces.controllers import (
    AuthControllerInterface,
    UserControllerInterface,
    ContextControllerInterface,
    DeviceControllerInterface,
    SensorControllerInterface,
)
from app.interfaces.repositories import (
    UserRepositoryInterface,
    ContextRepositoryInterface,
    DeviceRepositoryInterface,
    SensorRepositoryInterface,
)


class Container(containers.DeclarativeContainer):
    
    db = providers.Callable(SessionLocal)
    
    user_repository = providers.Factory(
        UserRepository,
        db=db
    )  # provides UserRepository (implements UserRepositoryInterface)

    context_repository = providers.Factory(
        ContextRepository,
        db=db
    )  # provides ContextRepository (implements ContextRepositoryInterface)
    
    device_repository = providers.Factory(
        DeviceRepository,
        db=db
    )  # provides DeviceRepository (implements DeviceRepositoryInterface)

    sensor_repository = providers.Factory(
        SensorRepository,
        db=db
    )  # provides SensorRepository (implements SensorRepositoryInterface)

    auth_service = providers.Factory(
        AuthService,
        user_repository=user_repository
    )  # implements AuthServiceInterface
    
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository
    )  # implements UserServiceInterface

    context_service = providers.Factory(
        ContextService,
        context_repository=context_repository
    )  # implements ContextServiceInterface
    
    device_service = providers.Factory(
        DeviceService,
        device_repository=device_repository
    )  # implements DeviceServiceInterface

    sensor_service = providers.Factory(
        SensorService,
        sensor_repository=sensor_repository,
        device_repository=device_repository
    )  # implements SensorServiceInterface

    auth_controller = providers.Factory(
        AuthController,
        db=db
    )  # implements AuthControllerInterface
    
    user_controller = providers.Factory(
        UserController,
        db=db
    )  # implements UserControllerInterface

    context_controller = providers.Factory(
        ContextController,
        db=db
    )  # implements ContextControllerInterface
    
    device_controller = providers.Factory(
        DeviceController,
        db=db
    )  # implements DeviceControllerInterface

    sensor_controller = providers.Factory(
        SensorController,
        db=db
    )  # implements SensorControllerInterface


container = Container()


def get_auth_controller() -> AuthControllerInterface:
    return container.auth_controller()


def get_user_controller() -> UserControllerInterface:
    return container.user_controller()


def get_context_controller() -> ContextControllerInterface:
    return container.context_controller()


def get_device_controller() -> DeviceControllerInterface:
    return container.device_controller()


def get_sensor_controller() -> SensorControllerInterface:
    return container.sensor_controller()
