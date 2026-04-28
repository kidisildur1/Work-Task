import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';
import { User } from '../types';

export function LoginPage() {
  const [users, setUsers] = useState<User[]>([]);
  useEffect(() => { apiGet<User[]>('/users').then(setUsers); }, []);
  return <div><h1>/login</h1><p>Тестовый вход через список сотрудников:</p><ul>{users.map(u => <li key={u.id}>{u.full_name}</li>)}</ul></div>;
}
