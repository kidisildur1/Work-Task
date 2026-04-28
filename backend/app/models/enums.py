from enum import Enum


class TaskStatus(str, Enum):
    NEW = "Новая"
    IN_PROGRESS = "В работе"
    WAITING_DATA = "Ожидает данных"
    NEEDS_CLARIFICATION = "Требует уточнения"
    IN_REVIEW = "На проверке"
    DONE = "Выполнена"
    POSTPONED = "Отложена"
    OVERDUE = "Просрочена"


class TaskPriority(str, Enum):
    LOW = "Низкий"
    MEDIUM = "Средний"
    HIGH = "Высокий"
    CRITICAL = "Критический"


class TaskSource(str, Enum):
    WEB = "Web"
    TELEGRAM_TEXT = "Telegram text"
    TELEGRAM_VOICE = "Telegram voice"
    TELEGRAM_FORWARDED = "Telegram forwarded message"
    MANUAL_IMPORT = "Manual import"
