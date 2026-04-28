from sqlalchemy.orm import Session
from app.models.entities import TaskHistory


def add_history(db: Session, task_id: int, action: str, details: str = "", actor_id: int | None = None, actor_name: str | None = None):
    entry = TaskHistory(
        task_id=task_id,
        action=action,
        details=details,
        actor_id=actor_id,
        actor_name_fallback=actor_name,
    )
    db.add(entry)
