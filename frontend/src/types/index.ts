export type Task = {
  id: number;
  title: string;
  description: string;
  status: string;
  priority: string;
  responsible_id: number | null;
  due_date: string | null;
  source: string;
  requires_clarification: boolean;
  progress_percent: number;
  project_id: number | null;
  tags: string[];
};

export type User = {
  id: number;
  full_name: string;
  title: string;
  email: string;
  telegram_username: string;
  total: number;
  in_progress: number;
  overdue: number;
  done: number;
  load: number;
};
