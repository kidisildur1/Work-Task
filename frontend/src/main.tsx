import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { KanbanPage } from './pages/KanbanPage';
import { LoginPage } from './pages/LoginPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { ProjectsPage } from './pages/ProjectsPage';
import { SettingsPage } from './pages/SettingsPage';
import { TaskDetailPage } from './pages/TaskDetailPage';
import { TasksPage } from './pages/TasksPage';
import { UsersPage } from './pages/UsersPage';
import './styles.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path='/login' element={<LoginPage />} />
        <Route path='/' element={<Layout />}>
          <Route index element={<Navigate to='/dashboard' />} />
          <Route path='dashboard' element={<DashboardPage />} />
          <Route path='tasks' element={<TasksPage />} />
          <Route path='tasks/:id' element={<TaskDetailPage />} />
          <Route path='kanban' element={<KanbanPage />} />
          <Route path='users' element={<UsersPage />} />
          <Route path='projects' element={<ProjectsPage />} />
          <Route path='notifications' element={<NotificationsPage />} />
          <Route path='settings' element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
