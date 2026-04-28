import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiGet, apiPatch, apiPost } from '../api/client';

export function TaskDetailPage() {
  const { id } = useParams();
  const [task, setTask] = useState<any>(null);
  const [comment, setComment] = useState('');
  const load = () => apiGet(`/tasks/${id}`).then(setTask);
  useEffect(load, [id]);
  if (!task) return <div>Загрузка...</div>;

  return <div>
    <h1>#{task.id} {task.title}</h1>
    <p>{task.description}</p>
    <div className='row'>
      <select value={task.status} onChange={async e=>{await apiPatch(`/tasks/${id}`, {status: e.target.value}); load();}}>
        {['Новая','В работе','Ожидает данных','Требует уточнения','На проверке','Выполнена','Отложена','Просрочена'].map(s => <option key={s}>{s}</option>)}
      </select>
      <select value={task.priority} onChange={async e=>{await apiPatch(`/tasks/${id}`, {priority: e.target.value}); load();}}>
        {['Низкий','Средний','Высокий','Критический'].map(s => <option key={s}>{s}</option>)}
      </select>
    </div>
    <h3>Комментарии</h3>
    <div className='row'><input value={comment} onChange={e=>setComment(e.target.value)} /><button onClick={async ()=>{await apiPost(`/tasks/${id}/comments`, {text: comment}); setComment(''); load();}}>Добавить</button></div>
    <ul>{task.comments.map((c:any)=><li key={c.id}>{c.text}</li>)}</ul>
    <h3>История</h3><ul>{task.history.map((h:any)=><li key={h.id}>{h.action}: {h.details}</li>)}</ul>
  </div>;
}
