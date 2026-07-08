from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from app.controllers.api_key_controller import ApiKeyController
from app.schemas.api_key import (
    ApiKeyCreateRequest,
    ApiKeyCreatedResponse,
    ApiKeyResponse,
)
from app.schemas.user import UserResponse
from app.core.container import get_api_key_controller
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post(
    "",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create API Key",
    description="Generate a new API Key for the authenticated user and return the raw key once",
)
def create_api_key(
    create_request: ApiKeyCreateRequest,
    current_user: UserResponse = Depends(get_current_user),
    controller: ApiKeyController = Depends(get_api_key_controller),
):
    api_key, raw_key = controller.create(current_user.id, create_request)
    return ApiKeyCreatedResponse(
        id=api_key.id,
        api_key=raw_key,
        permissions=api_key.permissions,
        created_at=api_key.created_at,
    )


@router.get(
    "",
    response_model=List[ApiKeyResponse],
    status_code=status.HTTP_200_OK,
    summary="List API Keys",
    description="List API Keys belonging to the authenticated user without exposing the key value",
)
def list_api_keys(
    current_user: UserResponse = Depends(get_current_user),
    controller: ApiKeyController = Depends(get_api_key_controller),
):
    return controller.list(current_user.id)


@router.delete(
    "/{api_key_id}",
    response_model=ApiKeyResponse,
    status_code=status.HTTP_200_OK,
    summary="Revoke API Key",
    description="Revoke an API Key owned by the authenticated user by setting revoked_at",
)
def revoke_api_key(
    api_key_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    controller: ApiKeyController = Depends(get_api_key_controller),
):
    return controller.revoke(api_key_id, current_user.id)


@router.post(
    "/{api_key_id}/rotate",
    response_model=ApiKeyCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Rotate API Key",
    description="Revoke an existing API Key and issue a new one preserving its permissions",
)
def rotate_api_key(
    api_key_id: UUID,
    current_user: UserResponse = Depends(get_current_user),
    controller: ApiKeyController = Depends(get_api_key_controller),
):
    api_key, raw_key = controller.rotate(api_key_id, current_user.id)
    return ApiKeyCreatedResponse(
        id=api_key.id,
        api_key=raw_key,
        permissions=api_key.permissions,
        created_at=api_key.created_at,
    )
