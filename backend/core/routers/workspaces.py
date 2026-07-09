from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.workspace_service import WorkspaceTask, workspace_service


router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class IntakeRequest(BaseModel):
    source_path: str = Field(..., description="Absolute path to the local project folder")
    prompt: str = ""
    requires_internet: bool = False


class TaskResponse(BaseModel):
    id: str
    source_path: str
    workspace_path: str
    prompt: str
    requires_internet: bool
    status: str
    created_at: str
    updated_at: str
    retry_count: int
    last_error: Optional[str] = None
    report_path: Optional[str] = None


class ProcessQueueResponse(BaseModel):
    processed: List[TaskResponse]


def _to_response(task: WorkspaceTask) -> TaskResponse:
    return TaskResponse(**task.__dict__)


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks() -> List[TaskResponse]:
    return [_to_response(task) for task in workspace_service.list_tasks()]


@router.post("/intake", response_model=TaskResponse, status_code=201)
async def intake_project(request: IntakeRequest) -> TaskResponse:
    try:
        task = workspace_service.enqueue_or_run(
            source_path=request.source_path,
            prompt=request.prompt,
            requires_internet=request.requires_internet,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _to_response(task)


@router.post("/tasks/process", response_model=ProcessQueueResponse)
async def process_queue() -> ProcessQueueResponse:
    processed = workspace_service.process_pending()
    return ProcessQueueResponse(processed=[_to_response(task) for task in processed])


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str) -> TaskResponse:
    task = workspace_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _to_response(task)
