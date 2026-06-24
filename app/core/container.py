from dependency_injector import containers, providers
from sqlalchemy.orm import Session
from app.settings.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.context_repository import ContextRepository
from app.repositories.device_repository import DeviceRepository
from app.repositories.sensor_repository import SensorRepository
from app.repositories.ingest_repository import IngestRepository
from app.repositories.api_key_repository import ApiKeyRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.context_service import ContextService
from app.services.device_service import DeviceService
from app.services.sensor_service import SensorService
from app.services.ingest_service import IngestService
from app.services.api_key_generator import ApiKeyGenerator
from app.services.api_key_service import ApiKeyService
from app.controllers.auth_controller import AuthController
from app.controllers.user_controller import UserController
from app.controllers.context_controller import ContextController
from app.controllers.device_controller import DeviceController
from app.controllers.sensor_controller import SensorController
from app.controllers.ingest_controller import IngestController
from app.controllers.api_key_controller import ApiKeyController
from app.interfaces.services import (
    AuthServiceInterface,
    UserServiceInterface,
    ContextServiceInterface,
    DeviceServiceInterface,
    SensorServiceInterface,
    IngestServiceInterface,
    ApiKeyServiceInterface,
)
from app.interfaces.controllers import (
    AuthControllerInterface,
    UserControllerInterface,
    ContextControllerInterface,
    DeviceControllerInterface,
    SensorControllerInterface,
    IngestControllerInterface,
    ApiKeyControllerInterface,
)
from app.interfaces.repositories import (
    UserRepositoryInterface,
    ContextRepositoryInterface,
    DeviceRepositoryInterface,
    SensorRepositoryInterface,
    IngestRepositoryInterface,
    ApiKeyRepositoryInterface,
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

    ingest_repository = providers.Factory(
        IngestRepository,
        db=db
    )

    api_key_repository = providers.Factory(
        ApiKeyRepository,
        db=db
    )

    api_key_generator = providers.Factory(
        ApiKeyGenerator
    )

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

    ingest_service = providers.Factory(
        IngestService,
        ingest_repository=ingest_repository,
        sensor_repository=sensor_repository
    )

    api_key_service = providers.Factory(
        ApiKeyService,
        api_key_repository=api_key_repository,
        api_key_generator=api_key_generator,
        user_repository=user_repository
    )

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

    ingest_controller = providers.Factory(
        IngestController,
        db=db
    )

    api_key_controller = providers.Factory(
        ApiKeyController,
        db=db
    )


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


def get_ingest_controller() -> IngestControllerInterface:
    return container.ingest_controller()


def get_api_key_controller() -> ApiKeyControllerInterface:
    return container.api_key_controller()
