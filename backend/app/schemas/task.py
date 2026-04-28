from datetime import date, datetime
from pydantic import BaseModel, Field
from typing import Literal


class ChecklistItem(BaseModel):
    text: str
    done: bool = False


class TaskBase(BaseModel):
    title: str
    description: str = ""
    summary: str = ""
    status: str = "Новая"
    priority: str = "Средний"
    responsible_id: int | None = None
    participant_ids: list[int] = Field(default_factory=list)
    due_date: date | None = None
    project_id: int | None = None
    source: str = "Web"
    tags: list[str] = Field(default_factory=list)
    requires_clarification: bool = False
    checklist: list[ChecklistItem] = Field(default_factory=list)
    progress_percent: int = 0
    links: list[str] = Field(default_factory=list)
    attachments: list[str] = Field(default_factory=list)


class TaskCreate(TaskBase):
    author_id: int | None = None
    author_name_fallback: str | None = None
    comment: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    summary: str | None = None
    status: str | None = None
    priority: str | None = None
    responsible_id: int | None = None
    participant_ids: list[int] | None = None
    due_date: date | None = None
    project_id: int | None = None
    tags: list[str] | None = None
    requires_clarification: bool | None = None
    checklist: list[ChecklistItem] | None = None
    progress_percent: int | None = None
    links: list[str] | None = None
    attachments: list[str] | None = None
    actor_id: int | None = None


class CommentCreate(BaseModel):
    author_id: int | None = None
    author_name_fallback: str | None = None
    text: str


class TelegramTaskIn(BaseModel):
    telegram_user_id: str | None = None
    username: str | None = None
    message_type: Literal["text", "voice"]
    text: str | None = None
    audio_file_url: str | None = None
    audio_file_id: str | None = None
    voice_file_id: str | None = None
    created_at: datetime | None = None


class TelegramTaskOut(BaseModel):
    success: bool
    task_id: int
    parsed_fields: dict
    requires_clarification: bool
    message: str
