-- Migration 002: Create tasks table
-- Run AFTER 001_create_users.sql

CREATE TYPE task_status   AS ENUM ('todo', 'in_progress', 'done');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high');

CREATE TABLE IF NOT EXISTS tasks (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title        TEXT NOT NULL,
  description  TEXT DEFAULT '',
  status       task_status   NOT NULL DEFAULT 'todo',
  priority     task_priority NOT NULL DEFAULT 'medium',
  due_date     DATE,
  creator_id   UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  assignee_id  UUID          REFERENCES users(id) ON DELETE SET NULL,
  created_at   TIMESTAMPTZ   NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ   NOT NULL DEFAULT now()
);

CREATE TRIGGER tasks_updated_at
  BEFORE UPDATE ON tasks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Indexes
CREATE INDEX IF NOT EXISTS idx_tasks_creator_id  ON tasks(creator_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_id ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status      ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at  ON tasks(created_at DESC);

-- Row-Level Security
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;

-- NOTE: Our Flask backend uses the service-role key (bypasses RLS).
-- RLS below is a defence-in-depth policy for direct DB access.
CREATE POLICY "users can see their own tasks" ON tasks
  FOR SELECT
  USING (
    creator_id  = auth.uid()
    OR assignee_id = auth.uid()
  );

CREATE POLICY "users can insert tasks they own" ON tasks
  FOR INSERT
  WITH CHECK (creator_id = auth.uid());

CREATE POLICY "creator or assignee can update" ON tasks
  FOR UPDATE
  USING (
    creator_id  = auth.uid()
    OR assignee_id = auth.uid()
  );

CREATE POLICY "only creator can delete" ON tasks
  FOR DELETE
  USING (creator_id = auth.uid());
