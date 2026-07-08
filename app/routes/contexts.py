from fastapi import APIRouter, Depends, status
from typing import Optional
from uuid import UUID
from app.controllers.context_controller import ContextController
from app.schemas.context import (
    ContextResponse,
    ContextCreateRequest,
    ContextUpdateRequest,
    ContextListResponse,
)
from app.core.container import get_context_controller

router = APIRouter(prefix="/contexts", tags=["contexts"])


@router.post("", response_model=ContextResponse, status_code=status.HTTP_201_CREATED)
def create_context(
    create_request: ContextCreateRequest,
    controller: ContextController = Depends(get_context_controller),
):
    return controller.create(create_request)


@router.get("", response_model=ContextListResponse, status_code=status.HTTP_200_OK)
def list_contexts(
    page: int = 1,
    limit: int = 10,
    name: Optional[str] = None,
    controller: ContextController = Depends(get_context_controller),
):
    items, total = controller.list(page=page, limit=limit, name=name)
    return {"items": items, "total": total, "page": page, "limit": limit}


@router.get("/{context_id}", response_model=ContextResponse, status_code=status.HTTP_200_OK)
def get_context(
    context_id: UUID,
    controller: ContextController = Depends(get_context_controller),
):
    return controller.get(context_id)


@router.put("/{context_id}", response_model=ContextResponse, status_code=status.HTTP_200_OK)
def update_context(
    context_id: UUID,
    update_request: ContextUpdateRequest,
    controller: ContextController = Depends(get_context_controller),
):
    return controller.update(context_id, update_request)


@router.delete("/{context_id}", status_code=status.HTTP_200_OK)
def delete_context(
    context_id: UUID,
    controller: ContextController = Depends(get_context_controller),
):
    controller.delete(context_id)
    return {"detail": "Context deleted"}
