import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Comment, Notification, Project, Task, TaskHistory, User
from app.models.enums import TaskPriority, TaskSource, TaskStatus
from app.schemas.task import CommentCreate, TaskCreate, TaskUpdate, TelegramTaskIn, TelegramTaskOut
from app.services.history import add_history
from app.services.speech_to_text import transcribe_voice
from app.services.task_parser import parse_task_text

router = APIRouter(prefix="/api")


def task_to_dict(task: Task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "summary": task.summary,
        "status": task.status.value,
        "priority": task.priority.value,
        "responsible_id": task.responsible_id,
        "participant_ids": json.loads(task.participants_json or "[]"),
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "project_id": task.project_id,
        "source": task.source.value,
        "author_id": task.author_id,
        "author_name_fallback": task.author_name_fallback,
        "telegram_original_text": task.telegram_original_text,
        "voice_transcript": task.voice_transcript,
        "audio_file_id": task.audio_file_id,
        "tags": json.loads(task.tags_json or "[]"),
        "requires_clarification": task.requires_clarification,
        "checklist": json.loads(task.checklist_json or "[]"),
        "progress_percent": task.progress_percent,
        "links": json.loads(task.links_json or "[]"),
        "attachments": json.loads(task.attachments_json or "[]"),
    }


@router.post("/login")
def login(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Сотрудник не найден")
    return {"token": f"demo-token-{user.id}", "user": {"id": user.id, "full_name": user.full_name}}


@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    response = []
    for u in users:
        total = db.query(func.count(Task.id)).filter(Task.responsible_id == u.id).scalar()
        in_progress = db.query(func.count(Task.id)).filter(Task.responsible_id == u.id, Task.status == TaskStatus.IN_PROGRESS).scalar()
        overdue = db.query(func.count(Task.id)).filter(Task.responsible_id == u.id, Task.status == TaskStatus.OVERDUE).scalar()
        done = db.query(func.count(Task.id)).filter(Task.responsible_id == u.id, Task.status == TaskStatus.DONE).scalar()
        response.append({
            "id": u.id,
            "full_name": u.full_name,
            "title": u.title,
            "email": u.email,
            "telegram_username": u.telegram_username,
            "total": total,
            "in_progress": in_progress,
            "overdue": overdue,
            "done": done,
            "load": min(100, (in_progress or 0) * 20),
        })
    return response


@router.get("/projects")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    out = []
    for p in projects:
        items = db.query(Task).filter(Task.project_id == p.id).all()
        total = len(items)
        overdue = len([t for t in items if t.status == TaskStatus.OVERDUE])
        done = len([t for t in items if t.status == TaskStatus.DONE])
        avg = round(sum([t.progress_percent for t in items]) / total, 1) if total else 0
        out.append({"id": p.id, "name": p.name, "total": total, "overdue": overdue, "done": done, "avg_progress": avg})
    return out


@router.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return [task_to_dict(t) for t in db.query(Task).order_by(Task.created_at.desc()).all()]


@router.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comments = db.query(Comment).filter(Comment.task_id == task_id).order_by(Comment.created_at.desc()).all()
    history = db.query(TaskHistory).filter(TaskHistory.task_id == task_id).order_by(TaskHistory.created_at.desc()).all()
    return {
        **task_to_dict(task),
        "comments": [{"id": c.id, "text": c.text, "created_at": c.created_at.isoformat(), "author_id": c.author_id, "author_name_fallback": c.author_name_fallback} for c in comments],
        "history": [{"id": h.id, "action": h.action, "details": h.details, "created_at": h.created_at.isoformat(), "actor_id": h.actor_id, "actor_name_fallback": h.actor_name_fallback} for h in history],
    }


@router.post("/tasks")
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(
        title=payload.title,
        description=payload.description,
        summary=payload.summary,
        status=TaskStatus(payload.status),
        priority=TaskPriority(payload.priority),
        responsible_id=payload.responsible_id,
        participants_json=json.dumps(payload.participant_ids, ensure_ascii=False),
        due_date=payload.due_date,
        project_id=payload.project_id,
        source=TaskSource(payload.source),
        author_id=payload.author_id,
        author_name_fallback=payload.author_name_fallback,
        tags_json=json.dumps(payload.tags, ensure_ascii=False),
        requires_clarification=payload.requires_clarification,
        checklist_json=json.dumps([i.model_dump() for i in payload.checklist], ensure_ascii=False),
        progress_percent=payload.progress_percent,
        links_json=json.dumps(payload.links, ensure_ascii=False),
        attachments_json=json.dumps(payload.attachments, ensure_ascii=False),
    )
    db.add(task)
    db.flush()
    add_history(db, task.id, "Создание задачи", "Задача создана вручную", payload.author_id, payload.author_name_fallback)
    if payload.comment:
        db.add(Comment(task_id=task.id, author_id=payload.author_id, author_name_fallback=payload.author_name_fallback, text=payload.comment))
        add_history(db, task.id, "Комментарий", "Добавлен комментарий при создании", payload.author_id, payload.author_name_fallback)
    db.add(Notification(type="task_created", title=f"Новая задача #{task.id}", message=task.title, task_id=task.id))
    db.commit()
    db.refresh(task)
    return task_to_dict(task)


@router.patch("/tasks/{task_id}")
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    actor_id = payload.actor_id
    if payload.title is not None:
        task.title = payload.title
    if payload.description is not None:
        task.description = payload.description
    if payload.summary is not None:
        task.summary = payload.summary
    if payload.status is not None:
        task.status = TaskStatus(payload.status)
        add_history(db, task.id, "Изменение статуса", f"Новый статус: {payload.status}", actor_id)
        if payload.status == TaskStatus.DONE.value:
            task.completed_at = datetime.utcnow()
    if payload.priority is not None:
        task.priority = TaskPriority(payload.priority)
        add_history(db, task.id, "Изменение приоритета", payload.priority, actor_id)
    if payload.responsible_id is not None:
        task.responsible_id = payload.responsible_id
        add_history(db, task.id, "Назначен ответственный", str(payload.responsible_id), actor_id)
    if payload.participant_ids is not None:
        task.participants_json = json.dumps(payload.participant_ids, ensure_ascii=False)
    if payload.due_date is not None:
        task.due_date = payload.due_date
        add_history(db, task.id, "Изменение срока", payload.due_date.isoformat(), actor_id)
    if payload.project_id is not None:
        task.project_id = payload.project_id
    if payload.tags is not None:
        task.tags_json = json.dumps(payload.tags, ensure_ascii=False)
    if payload.requires_clarification is not None:
        task.requires_clarification = payload.requires_clarification
    if payload.checklist is not None:
        task.checklist_json = json.dumps([i.model_dump() for i in payload.checklist], ensure_ascii=False)
    if payload.progress_percent is not None:
        task.progress_percent = payload.progress_percent
    if payload.links is not None:
        task.links_json = json.dumps(payload.links, ensure_ascii=False)
    if payload.attachments is not None:
        task.attachments_json = json.dumps(payload.attachments, ensure_ascii=False)

    db.commit()
    db.refresh(task)
    return task_to_dict(task)


@router.post("/tasks/{task_id}/comments")
def add_comment(task_id: int, payload: CommentCreate, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    c = Comment(task_id=task_id, author_id=payload.author_id, author_name_fallback=payload.author_name_fallback, text=payload.text)
    db.add(c)
    add_history(db, task_id, "Добавлен комментарий", payload.text[:120], payload.author_id, payload.author_name_fallback)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "text": c.text, "created_at": c.created_at.isoformat()}


@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    today = date.today()
    stats = {
        "total": len(tasks),
        "new": len([t for t in tasks if t.status == TaskStatus.NEW]),
        "in_progress": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS]),
        "in_review": len([t for t in tasks if t.status == TaskStatus.IN_REVIEW]),
        "done": len([t for t in tasks if t.status == TaskStatus.DONE]),
        "overdue": len([t for t in tasks if (t.due_date and t.due_date < today and t.status != TaskStatus.DONE) or t.status == TaskStatus.OVERDUE]),
        "without_responsible": len([t for t in tasks if not t.responsible_id]),
        "needs_clarification": len([t for t in tasks if t.requires_clarification]),
    }
    recent = [task_to_dict(t) for t in db.query(Task).order_by(Task.created_at.desc()).limit(5).all()]
    deadlines = [task_to_dict(t) for t in db.query(Task).filter(Task.due_date.isnot(None)).order_by(Task.due_date.asc()).limit(5).all()]
    load = []
    for user in db.query(User).all():
        count = db.query(func.count(Task.id)).filter(Task.responsible_id == user.id, Task.status.in_([TaskStatus.NEW, TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW])).scalar()
        load.append({"user": user.full_name, "active_tasks": count})
    return {"stats": stats, "recent_changes": recent, "deadlines": deadlines, "employee_load": load}


@router.get("/notifications")
def list_notifications(db: Session = Depends(get_db)):
    rows = db.query(Notification).order_by(Notification.created_at.desc()).limit(50).all()
    return [{"id": n.id, "type": n.type, "title": n.title, "message": n.message, "task_id": n.task_id, "created_at": n.created_at.isoformat()} for n in rows]


@router.post("/tasks/from-telegram", response_model=TelegramTaskOut)
def create_from_telegram(payload: TelegramTaskIn, db: Session = Depends(get_db)):
    author = None
    if payload.telegram_user_id:
        author = db.query(User).filter(User.telegram_user_id == payload.telegram_user_id).first()
    if not author and payload.username:
        author = db.query(User).filter(User.telegram_username == payload.username).first()

    text = payload.text or ""
    voice_transcript = None
    source = TaskSource.TELEGRAM_TEXT if payload.message_type == "text" else TaskSource.TELEGRAM_VOICE
    if payload.message_type == "voice":
        voice_transcript = transcribe_voice(payload.audio_file_id, payload.voice_file_id)
        text = text or voice_transcript

    parsed = parse_task_text(text)

    responsible_id = None
    if parsed.get("responsible_name"):
        candidate = db.query(User).filter(User.full_name.ilike(f"%{parsed['responsible_name']}%")).first()
        if candidate:
            responsible_id = candidate.id

    project_id = None
    if parsed.get("project_name"):
        project = db.query(Project).filter(Project.name == parsed["project_name"]).first()
        if project:
            project_id = project.id

    due_date = date.fromisoformat(parsed["due_date"]) if parsed.get("due_date") else None

    task = Task(
        title=parsed["title"][:255],
        description=parsed["description"],
        summary=parsed["title"][:255],
        status=TaskStatus.NEW,
        priority=TaskPriority(parsed["priority"]),
        responsible_id=responsible_id,
        participants_json="[]",
        due_date=due_date,
        project_id=project_id,
        source=source,
        author_id=author.id if author else None,
        author_name_fallback=(author.full_name if author else "Неизвестный Telegram-пользователь"),
        telegram_original_text=payload.text,
        voice_transcript=voice_transcript,
        audio_file_id=payload.audio_file_id or payload.voice_file_id,
        tags_json=json.dumps(parsed.get("tags", []), ensure_ascii=False),
        requires_clarification=parsed["requires_clarification"],
        checklist_json="[]",
        progress_percent=0,
    )
    db.add(task)
    db.flush()
    add_history(db, task.id, "Создано из Telegram", payload.message_type, task.author_id, task.author_name_fallback)
    db.add(Notification(type="telegram_task", title=f"Задача из Telegram #{task.id}", message=task.title, task_id=task.id))
    db.commit()

    return TelegramTaskOut(
        success=True,
        task_id=task.id,
        parsed_fields=parsed,
        requires_clarification=parsed["requires_clarification"],
        message="Задача создана, но требует уточнения" if parsed["requires_clarification"] else "Задача создана успешно",
    )
