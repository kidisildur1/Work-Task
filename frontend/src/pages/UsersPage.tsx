import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';
import { User } from '../types';

export function UsersPage(){
  const [users,setUsers]=useState<User[]>([]);
  useEffect(()=>{apiGet<User[]>('/users').then(setUsers)},[]);
  return <div><h1>Сотрудники лаборатории</h1><table><thead><tr><th>ФИО</th><th>Должность</th><th>Email</th><th>Telegram</th><th>Всего</th><th>В работе</th><th>Просрочено</th></tr></thead><tbody>{users.map(u=><tr key={u.id}><td>{u.full_name}</td><td>{u.title}</td><td>{u.email}</td><td>@{u.telegram_username}</td><td>{u.total}</td><td>{u.in_progress}</td><td>{u.overdue}</td></tr>)}</tbody></table></div>
}
