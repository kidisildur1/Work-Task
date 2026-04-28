import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';

export function DashboardPage() {
  const [data, setData] = useState<any>(null);
  useEffect(() => { apiGet('/dashboard').then(setData); }, []);
  if (!data) return <div>Загрузка...</div>;
  return <div>
    <h1>Dashboard</h1>
    <div className='cards'>{Object.entries(data.stats).map(([k,v]) => <div key={k} className='card'><b>{String(v)}</b><div>{k}</div></div>)}</div>
    <h3>Ближайшие дедлайны</h3>
    <ul>{data.deadlines.map((t:any)=><li key={t.id}>#{t.id} {t.title} — {t.due_date}</li>)}</ul>
  </div>;
}
