import json
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.entities import Comment, Notification, Project, Task, User
from app.models.enums import TaskPriority, TaskSource, TaskStatus


def seed_data(db: Session):
    if db.query(User).count() > 0:
        return

    users = [
        User(full_name="Иванов Денис Сергеевич", title="Инженер-моделировщик", telegram_username="denis_model", telegram_user_id="10001", email="denis@lab.local"),
        User(full_name="Петрова Анна Викторовна", title="Старший научный сотрудник", telegram_username="anna_lab", telegram_user_id="10002", email="anna@lab.local"),
        User(full_name="Смирнов Илья Павлович", title="Руководитель направления QForm", telegram_username="ilya_qform", telegram_user_id="10003", email="ilya@lab.local"),
        User(full_name="Козлова Мария Олеговна", title="Инженер-расчетчик", telegram_username="maria_calc", telegram_user_id="10004", email="maria@lab.local"),
    ]
    db.add_all(users)
    db.flush()

    project_names = [
        "Моделирование процессов прошивки",
        "Редукционно-растяжной стан",
        "Калибрование концов труб",
        "QForm-моделирование",
        "Охрана труда / обучение",
        "Отчеты и презентации",
        "Производственные задачи",
        "Диссертация / научная работа",
        "Публикации и конференции",
        "Прочее",
    ]
    projects = [Project(name=n, description=n) for n in project_names]
    db.add_all(projects)
    db.flush()

    tasks_payload = [
        ("Подготовить модель калибрования конца трубы 244,48×8,94", TaskStatus.NEW, TaskPriority.HIGH, 1, 3, TaskSource.WEB, False),
        ("Проверить влияние угла конусности инструмента на среднюю овальность", TaskStatus.IN_PROGRESS, TaskPriority.CRITICAL, 2, 3, TaskSource.TELEGRAM_TEXT, False),
        ("Сформировать презентацию по результатам моделирования", TaskStatus.IN_REVIEW, TaskPriority.MEDIUM, 1, 6, TaskSource.WEB, False),
        ("Провести расчет напряженно-деформированного состояния при редуцировании", TaskStatus.WAITING_DATA, TaskPriority.HIGH, 4, 2, TaskSource.WEB, True),
        ("Подготовить отчет по эксперименту для ЧТПЗ", TaskStatus.DONE, TaskPriority.MEDIUM, 2, 6, TaskSource.TELEGRAM_VOICE, False),
        ("Проверить исходные данные для QForm-модели", TaskStatus.OVERDUE, TaskPriority.HIGH, 3, 4, TaskSource.TELEGRAM_TEXT, True),
        ("Сформировать матрицу компьютерного эксперимента", TaskStatus.NEW, TaskPriority.MEDIUM, None, 1, TaskSource.WEB, True),
        ("Подготовить материалы по редукционно-растяжному стану", TaskStatus.IN_PROGRESS, TaskPriority.HIGH, 1, 2, TaskSource.WEB, False),
        ("Проверить результаты по средней овальности", TaskStatus.POSTPONED, TaskPriority.LOW, 2, 3, TaskSource.TELEGRAM_VOICE, False),
        ("Подготовить слайды по научной новизне", TaskStatus.IN_PROGRESS, TaskPriority.MEDIUM, 3, 8, TaskSource.WEB, False),
        ("Оформить план обучения по охране труда", TaskStatus.NEW, TaskPriority.LOW, 4, 5, TaskSource.MANUAL_IMPORT, False),
        ("Собрать данные по производственной партии №47", TaskStatus.NEEDS_CLARIFICATION, TaskPriority.HIGH, None, 7, TaskSource.TELEGRAM_TEXT, True),
    ]

    for i, (title, status, priority, responsible_id, project_id, source, clarify) in enumerate(tasks_payload, 1):
        due = date.today() + timedelta(days=(i - 6))
        task = Task(
            title=title,
            description=title + " — детальное описание задачи.",
            summary=title[:120],
            status=status,
            priority=priority,
            responsible_id=responsible_id,
            participants_json=json.dumps([u.id for u in users[:2]]),
            due_date=due,
            project_id=project_id,
            source=source,
            author_id=users[0].id,
            author_name_fallback=users[0].full_name,
            telegram_original_text=title if "Telegram" in source.value else None,
            voice_transcript="Тестовая расшифровка" if source == TaskSource.TELEGRAM_VOICE else None,
            tags_json=json.dumps(["лаборатория", "моделирование"]),
            requires_clarification=clarify,
            checklist_json=json.dumps([
                {"text": "Собрать данные", "done": True},
                {"text": "Провести расчет", "done": False},
            ], ensure_ascii=False),
            progress_percent=50 if status in [TaskStatus.IN_PROGRESS, TaskStatus.IN_REVIEW] else (100 if status == TaskStatus.DONE else 20),
            links_json=json.dumps(["https://example.com/qform"]),
            attachments_json=json.dumps(["report.xlsx"]),
        )
        db.add(task)
        db.flush()
        db.add(Comment(task_id=task.id, author_id=users[1].id, text="Проверил входные параметры, продолжаю работу."))
        db.add(Notification(type="task_created", title=f"Новая задача #{task.id}", message=task.title, task_id=task.id))

    db.commit()
