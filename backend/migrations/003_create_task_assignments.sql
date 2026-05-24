-- Migration 003: Task assignment audit log
-- Run AFTER 002_create_tasks.sql

CREATE TABLE IF NOT EXISTS task_assignments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id     UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  assigned_to UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  assigned_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  assigned_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ta_task_id     ON task_assignments(task_id);
CREATE INDEX IF NOT EXISTS idx_ta_assigned_to ON task_assignments(assigned_to);

ALTER TABLE task_assignments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "parties can see assignment history" ON task_assignments
  FOR SELECT
  USING (
    assigned_to = auth.uid()
    OR assigned_by = auth.uid()
  );
