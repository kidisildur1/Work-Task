import { useEffect, useState } from 'react';
import { apiGet } from '../api/client';

export function NotificationsPage(){
  const [rows,setRows]=useState<any[]>([]);
  useEffect(()=>{apiGet<any[]>('/notifications').then(setRows)},[]);
  return <div><h1>Уведомления</h1><ul>{rows.map(n=><li key={n.id}>{n.title} — {n.message}</li>)}</ul></div>
}
