const KEY = 'work-task-demo';
const now = () => new Date().toISOString();
const day = (n: number) => { const d = new Date(); d.setDate(d.getDate() + n); return d.toISOString().slice(0, 10); };

const seed: any = {
  users: [
    { id: 1, full_name: 'Denis Akhmerov', title: 'Deputy lab head', email: 'denis@example.com', telegram_username: 'denis_lab' },
    { id: 2, full_name: 'Sergey Ivanov', title: 'Research engineer', email: 'ivanov@example.com', telegram_username: 'ivanov_model' },
    { id: 3, full_name: 'Anna Petrova', title: 'Engineer', email: 'petrova@example.com', telegram_username: 'petrova_calc' }
  ],
  projects: [
    { id: 1, name: 'Pipe end calibration' },
    { id: 2, name: 'Stretch-reducing mill' },
    { id: 3, name: 'QForm modelling' },
    { id: 4, name: 'Reports and presentations' }
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
    comments: [{ id: 1, text: 'Demo comment', created_at: now(), author_id: 1 }],
    history: [{ id: 1, action: 'Task created', details: source, created_at: now(), actor_id: 1 }]
  };
}

seed.tasks = [
  makeTask(1, 'Prepare model for pipe end calibration 244.48x8.94', 'In progress', 'High', 1, 1, 'Web', 3, 45),
  makeTask(2, 'Check cone angle effect on average ovality', 'Review', 'Critical', 2, 1, 'Telegram text', 1, 80),
  makeTask(3, 'Prepare modelling results presentation', 'New', 'Medium', 3, 4, 'Web', 7, 10),
  makeTask(4, 'Run stress-strain calculation for reducing process', 'In progress', 'High', 2, 2, 'Telegram voice', 5, 55),
  makeTask(5, 'Prepare experiment report for plant', 'Waiting for data', 'Medium', 1, 4, 'Web', 10, 35, true),
  makeTask(6, 'Check QForm input data', 'Overdue', 'High', 2, 3, 'Manual import', -2, 20, true),
  makeTask(7, 'Prepare full-factorial experiment matrix', 'Done', 'Medium', 3, 1, 'Web', -1, 100),
  makeTask(8, 'Prepare materials for stretch-reducing mill', 'In progress', 'Medium', 1, 2, 'Telegram text', 14, 40),
  makeTask(9, 'Check average ovality results', 'Needs clarification', 'Critical', null, 1, 'Telegram voice', 2, 15, true),
  makeTask(10, 'Prepare scientific novelty slides', 'Deferred', 'Low', 1, 4, 'Web', 20, 5)
];
seed.notifications = [
  { id: 1, type: 'task_created', title: 'New task', message: seed.tasks[0].title, task_id: 1, created_at: now() },
  { id: 2, type: 'telegram_task', title: 'Telegram task', message: seed.tasks[1].title, task_id: 2, created_at: now() }
];

function db() { const raw = localStorage.getItem(KEY); if (raw) return JSON.parse(raw); localStorage.setItem(KEY, JSON.stringify(seed)); return JSON.parse(JSON.stringify(seed)); }
function save(x: any) { localStorage.setItem(KEY, JSON.stringify(x)); }
function overdue(t: any) { return t.status === 'Overdue' || (t.due_date && t.due_date < day(0) && t.status !== 'Done'); }

export async function demoGet(path: string): Promise<any> {
  const x = db();
  if (path === '/tasks') return x.tasks;
  if (path.startsWith('/tasks/')) { const t = x.tasks.find((z: any) => z.id === Number(path.split('/')[2])); return { ...t, comments: t.comments || [], history: t.history || [] }; }
  if (path === '/users') return x.users.map((u: any) => { const a = x.tasks.filter((t: any) => t.responsible_id === u.id); return { ...u, total: a.length, in_progress: a.filter((t: any) => t.status === 'In progress').length, overdue: a.filter(overdue).length, done: a.filter((t: any) => t.status === 'Done').length, load: Math.min(100, a.length * 20) }; });
  if (path === '/projects') return x.projects.map((p: any) => { const a = x.tasks.filter((t: any) => t.project_id === p.id); return { ...p, total: a.length, overdue: a.filter(overdue).length, done: a.filter((t: any) => t.status === 'Done').length, avg_progress: a.length ? Math.round(a.reduce((s: number, t: any) => s + t.progress_percent, 0) / a.length) : 0 }; });
  if (path === '/notifications') return x.notifications;
  if (path === '/dashboard') return { stats: { total: x.tasks.length, new: x.tasks.filter((t: any) => t.status === 'New').length, in_progress: x.tasks.filter((t: any) => t.status === 'In progress').length, in_review: x.tasks.filter((t: any) => t.status === 'Review').length, done: x.tasks.filter((t: any) => t.status === 'Done').length, overdue: x.tasks.filter(overdue).length, without_responsible: x.tasks.filter((t: any) => !t.responsible_id).length, needs_clarification: x.tasks.filter((t: any) => t.requires_clarification).length }, recent_changes: x.tasks.slice(0, 5), deadlines: x.tasks.slice(0, 5), employee_load: [] };
  return null;
}

export async function demoPost(path: string, body: any): Promise<any> {
  const x = db();
  if (path === '/tasks') { const id = Math.max(...x.tasks.map((t: any) => t.id), 0) + 1; const t = makeTask(id, body.title || 'New task', body.status || 'New', body.priority || 'Medium', body.responsible_id || null, body.project_id || 1, body.source || 'Web', 7, 0, !body.responsible_id); x.tasks.unshift(t); save(x); return t; }
  if (path.endsWith('/comments')) { const id = Number(path.split('/')[2]); const t = x.tasks.find((z: any) => z.id === id); const c = { id: Date.now(), text: body.text, created_at: now(), author_id: 1 }; t.comments.push(c); save(x); return c; }
}

export async function demoPatch(path: string, body: any): Promise<any> {
  const x = db(); const id = Number(path.split('/')[2]); const t = x.tasks.find((z: any) => z.id === id); Object.assign(t, body); t.history.push({ id: Date.now(), action: 'Task updated', details: JSON.stringify(body), created_at: now(), actor_id: 1 }); save(x); return t;
}
