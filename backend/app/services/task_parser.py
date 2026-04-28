import re
from datetime import date, timedelta

PRIORITY_KEYWORDS = {
    "крит": "Критический",
    "высок": "Высокий",
    "средн": "Средний",
    "низк": "Низкий",
}


def _next_weekday(target_weekday: int) -> date:
    today = date.today()
    days_ahead = (target_weekday - today.weekday()) % 7
    days_ahead = 7 if days_ahead == 0 else days_ahead
    return today + timedelta(days=days_ahead)


def parse_task_text(text: str) -> dict:
    normalized = (text or "").strip()
    lower = normalized.lower()
    due_date = None
    if "пятниц" in lower:
        due_date = _next_weekday(4)
    elif "понедель" in lower:
        due_date = _next_weekday(0)

    priority = "Средний"
    for key, value in PRIORITY_KEYWORDS.items():
        if key in lower:
            priority = value
            break

    responsible_name = None
    match = re.search(r"ответственн(?:ый|ая)?\s+([А-Яа-яA-Za-z]+)", normalized)
    if match:
        responsible_name = match.group(1)

    title = normalized
    m2 = re.search(r"(проверить|подготовить|сформировать|провести|поставь задачу)\s+(.+)", lower)
    if m2:
        action = m2.group(1).capitalize()
        body = m2.group(2).split(",")[0]
        title = f"{action} {body}"[:255]

    tags = []
    if "qform" in lower:
        tags.append("QForm")
    if "овальност" in lower:
        tags.append("Овальность")
    if "редуц" in lower:
        tags.append("Редуцирование")

    project = None
    if "калибр" in lower:
        project = "Калибрование концов труб"
    elif "редук" in lower:
        project = "Редукционно-растяжной стан"
    elif "qform" in lower:
        project = "QForm-моделирование"

    missing = []
    if not responsible_name:
        missing.append("ответственный")
    if not due_date:
        missing.append("срок")

    return {
        "title": title,
        "description": normalized,
        "priority": priority,
        "due_date": due_date.isoformat() if due_date else None,
        "responsible_name": responsible_name,
        "project_name": project,
        "tags": tags,
        "missing_fields": missing,
        "requires_clarification": len(missing) > 0,
    }
