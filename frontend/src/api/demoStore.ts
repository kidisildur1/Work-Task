const KEY = 'work-task-demo-v3';
const now = () => new Date().toISOString();
const day = (n: number) => { const d = new Date(); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };

const seed: any = {
  users: [
    { id: 1, full_name: 'Ахмеров Денис Альфредович', title: 'Заместитель начальника лаборатории', email: 'denis@example.com', telegram_username: 'denis_lab' },
    { id: 2, full_name: 'Иванов Сергей Петрович', title: 'Научный сотрудник', email: 'ivanov@example.com', telegram_username: 'ivanov_model' },
    { id: 3, full_name: 'Петрова Анна Игоревна', title: 'Инженер-исследователь', email: 'petrova@example.com', telegram_username: 'petrova_calc' }
  ],
  projects: [
    { id: 1, name: 'Калибрование концов труб' },
    { id: 2, name: 'Редукционно-растяжной стан' },
    { id: 3, name: 'QForm-моделирование' },
    { id: 4, name: 'Отчеты и презентации' }
  ],
  tasks: [],
  notifications: []
};

function makeTask(id: number, title: string, status: string, priority: string, responsible_id: number | null, project_id: number, source: string, offset: number, progress: number, requires_clarification = false) {
  return {
    id, title, description: title, summary: title, status, priority, responsible_id, participant_ids: [],
    created_at: now(), due_date: day(offset), completed_at: null, project_id, source, author_id: 1,
    author_name_fallback: 'Demo user', telegram_original_text: source.includes('Telegram') ? title : null,
    voice_transcript: source === 'Telegram voice' ? title : null, audio_file_id: null, tags: [],
    requires_clarification, checklist: [], progress_percent: progress, links: [], attachments: [],
    comments: [{ id: 1, text: 'Демо-комментарий', created_at: now(), author_id: 1 }],
    history: [{ id: 1, action: 'Создание задачи', details: source, created_at: now(), actor_id: 1 }]
  };
}

seed.tasks = [
  makeTask(1, 'Подготовить модель калибрования конца трубы 244,48x8,94', 'В работе', 'Высокий', 1, 1, 'Web', 3, 45),
  makeTask(2, 'Проверить влияние угла конусности на среднюю овальность', 'На проверке', 'Критический', 2, 1, 'Telegram text', 1, 80),
  makeTask(3, 'Сформировать презентацию по результатам моделирования', 'Новая', 'Средний', 3, 4, 'Web', 7, 10),
  makeTask(4, 'Провести расчет НДС при редуцировании', 'В работе', 'Высокий', 2, 2, 'Telegram voice', 5, 55),
  makeTask(5, 'Подготовить отчет по эксперименту для ЧТПЗ', 'Ожидает данных', 'Средний', 1, 4, 'Web', 10, 35, true),
  makeTask(6, 'Проверить исходные данные для QForm-модели', 'Просрочена', 'Высокий', 2, 3, 'Manual import', -2, 20, true),
  makeTask(7, 'Сформировать матрицу компьютерного эксперимента', 'Выполнена', 'Средний', 3, 1, 'Web', -1, 100),
  makeTask(8, 'Подготовить материалы по редукционно-растяжному стану', 'В работе', 'Средний', 1, 2, 'Telegram text', 14, 40),
  makeTask(9, 'Проверить результаты по средней овальности', 'Требует уточнения', 'Критический', null, 1, 'Telegram voice', 2, 15, true),
  makeTask(10, 'Подготовить слайды по научной новизне', 'Отложена', 'Низкий', 1, 4, 'Web', 20, 5)
];
seed.notifications = [
  { id: 1, type: 'task_created', title: 'Новая задача', message: seed.tasks[0].title, task_id: 1, created_at: now() },
  { id: 2, type: 'telegram_task', title: 'Задача из Telegram', message: seed.tasks[1].title, task_id: 2, created_at: now() }
];

function db() { const raw = localStorage.getItem(KEY); if (raw) return JSON.parse(raw); localStorage.setItem(KEY, JSON.stringify(seed)); return JSON.parse(JSON.stringify(seed)); }
function save(x: any) { localStorage.setItem(KEY, JSON.stringify(x)); }
function overdue(t: any) { return t.status === 'Просрочена' || (t.due_date && t.due_date < day(0) && t.status !== 'Выполнена'); }

export async function demoGet(path: string): Promise<any> {
  const x = db();
  if (path === '/tasks') return x.tasks;
  if (path.startsWith('/tasks/')) { const t = x.tasks.find((z: any) => z.id === Number(path.split('/')[2])); return { ...t, comments: t.comments || [], history: t.history || [] }; }
  if (path === '/users') return x.users.map((u: any) => { const a = x.tasks.filter((t: any) => t.responsible_id === u.id); return { ...u, total: a.length, in_progress: a.filter((t: any) => t.status === 'В работе').length, overdue: a.filter(overdue).length, done: a.filter((t: any) => t.status === 'Выполнена').length, load: Math.min(100, a.length * 20) }; });
  if (path === '/projects') return x.projects.map((p: any) => { const a = x.tasks.filter((t: any) => t.project_id === p.id); return { ...p, total: a.length, overdue: a.filter(overdue).length, done: a.filter((t: any) => t.status === 'Выполнена').length, avg_progress: a.length ? Math.round(a.reduce((s: number, t: any) => s + t.progress_percent, 0) / a.length) : 0 }; });
  if (path === '/notifications') return x.notifications;
  if (path === '/dashboard') return { stats: { total: x.tasks.length, new: x.tasks.filter((t: any) => t.status === 'Новая').length, in_progress: x.tasks.filter((t: any) => t.status === 'В работе').length, in_review: x.tasks.filter((t: any) => t.status === 'На проверке').length, done: x.tasks.filter((t: any) => t.status === 'Выполнена').length, overdue: x.tasks.filter(overdue).length, without_responsible: x.tasks.filter((t: any) => !t.responsible_id).length, needs_clarification: x.tasks.filter((t: any) => t.requires_clarification).length }, recent_changes: x.tasks.slice(0, 5), deadlines: x.tasks.slice(0, 5), employee_load: [] };
  return null;
}

export async function demoPost(path: string, body: any): Promise<any> {
  const x = db();
  if (path === '/tasks') { const id = Math.max(...x.tasks.map((t: any) => t.id), 0) + 1; const t = makeTask(id, body.title || 'Новая задача', body.status || 'Новая', body.priority || 'Средний', body.responsible_id || null, body.project_id || 1, body.source || 'Web', 7, 0, !body.responsible_id); x.tasks.unshift(t); save(x); return t; }
  if (path.endsWith('/comments')) { const id = Number(path.split('/')[2]); const t = x.tasks.find((z: any) => z.id === id); const c = { id: Date.now(), text: body.text, created_at: now(), author_id: 1 }; t.comments.push(c); save(x); return c; }
}

export async function demoPatch(path: string, body: any): Promise<any> {
  const x = db(); const id = Number(path.split('/')[2]); const t = x.tasks.find((z: any) => z.id === id); Object.assign(t, body); t.history.push({ id: Date.now(), action: 'Изменение задачи', details: JSON.stringify(body), created_at: now(), actor_id: 1 }); save(x); return t;
}
