import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet, apiPost } from '../api/client';
import { Task } from '../types';

export function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const load = () => apiGet<Task[]>('/tasks').then(setTasks);
  useEffect(load, []);

  const create = async () => {
    await apiPost('/tasks', { title, description: title, priority: 'Средний', status: 'Новая', source: 'Web', participant_ids: [], tags: [], checklist: [], links: [], attachments: [] });
    setTitle('');
    load();
  };

  return <div>
    <h1>Задачи /tasks</h1>
    <div className='row'><input value={title} onChange={e=>setTitle(e.target.value)} placeholder='Новая задача' /><button onClick={create}>Создать быстро</button></div>
    <table><thead><tr><th>ID</th><th>Задача</th><th>Статус</th><th>Приоритет</th><th>Срок</th><th>Источник</th></tr></thead><tbody>
      {tasks.map(t=><tr key={t.id}><td>{t.id}</td><td><Link to={`/tasks/${t.id}`}>{t.title}</Link></td><td>{t.status}</td><td><span className={`badge priority-${t.priority}`}>{t.priority}</span></td><td>{t.due_date ?? '-'}</td><td>{t.source}</td></tr>)}
    </tbody></table>
  </div>;
}
