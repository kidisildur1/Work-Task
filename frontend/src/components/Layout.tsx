import { Link, Outlet } from 'react-router-dom';

export function Layout() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h3>Lab Tasks</h3>
        {['/dashboard','/tasks','/kanban','/users','/projects','/notifications','/settings'].map(p => (
          <Link key={p} to={p}>{p.replace('/','')}</Link>
        ))}
      </aside>
      <main className="main"><Outlet /></main>
    </div>
  );
}
