import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';

export function ProjectsPage(){
  const [rows,setRows]=useState<any[]>([]);
  useEffect(()=>{apiGet<any[]>('/projects').then(setRows)},[]);
  return <div><h1>Проекты / направления</h1><table><thead><tr><th>Направление</th><th>Всего</th><th>Просрочено</th><th>Выполнено</th><th>Средний прогресс</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><td>{r.name}</td><td>{r.total}</td><td>{r.overdue}</td><td>{r.done}</td><td>{r.avg_progress}%</td></tr>)}</tbody></table></div>
}
