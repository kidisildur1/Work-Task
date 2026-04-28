import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';
import { Task } from '../types';

const columns = ['Новая','В работе','Ожидает данных','Требует уточнения','На проверке','Выполнена','Отложена'];
export function KanbanPage(){
  const [tasks,setTasks]=useState<Task[]>([]);
  useEffect(()=>{apiGet<Task[]>('/tasks').then(setTasks)},[]);
  return <div><h1>Kanban</h1><div className='row' style={{alignItems:'flex-start'}}>{columns.map(c=><div key={c} className='card' style={{minWidth:220}}><h4>{c}</h4>{tasks.filter(t=>t.status===c).map(t=><div key={t.id} className='card'><b>{t.title}</b><div>{t.priority} · {t.source}</div></div>)}</div>)}</div></div>
}
