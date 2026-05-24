"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { CreateTaskPayload, UpdateTaskPayload, User, Task } from "@/types";
import { cn } from "@/lib/utils";

interface TaskFormProps {
  mode: "create" | "edit";
  initial?: Partial<Task>;
  users: User[];
  currentUserId: string;
  onSubmit: (data: CreateTaskPayload | UpdateTaskPayload) => Promise<void>;
  onClose: () => void;
}

export function TaskForm({ mode, initial, users, currentUserId, onSubmit, onClose }: TaskFormProps) {
  const [title, setTitle] = useState(initial?.title ?? "");
  const [description, setDescription] = useState(initial?.description ?? "");
  const [priority, setPriority] = useState<Task["priority"]>(initial?.priority ?? "medium");
  const [status, setStatus] = useState<Task["status"]>(initial?.status ?? "todo");
  const [dueDate, setDueDate] = useState(initial?.due_date ?? "");
  const [assigneeId, setAssigneeId] = useState(initial?.assignee_id ?? "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) { setError("Title is required"); return; }
    setLoading(true);
    setError("");
    try {
      await onSubmit({
        title: title.trim(),
        description,
        priority,
        status,
        due_date: dueDate || undefined,
        assignee_id: assigneeId || undefined,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-ink/40 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-lg card p-6 animate-slide-up">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold text-ink font-display">
            {mode === "create" ? "New task" : "Edit task"}
          </h2>
          <button onClick={onClose} className="btn-ghost p-1.5">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="label">Title *</label>
            <input
              className="input"
              placeholder="What needs to be done?"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoFocus
            />
          </div>

          <div>
            <label className="label">Description</label>
            <textarea
              className="input resize-none h-20"
              placeholder="Add more details…"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Priority</label>
              <select
                className="select"
                value={priority}
                onChange={(e) => setPriority(e.target.value as Task["priority"])}
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>

            {mode === "edit" && (
              <div>
                <label className="label">Status</label>
                <select
                  className="select"
                  value={status}
                  onChange={(e) => setStatus(e.target.value as Task["status"])}
                >
                  <option value="todo">To do</option>
                  <option value="in_progress">In progress</option>
                  <option value="done">Done</option>
                </select>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Due date</label>
              <input
                type="date"
                className="input"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
              />
            </div>

            <div>
              <label className="label">Assign to</label>
              <select
                className="select"
                value={assigneeId}
                onChange={(e) => setAssigneeId(e.target.value)}
              >
                <option value="">Unassigned</option>
                {users.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name || u.email} {u.id === currentUserId ? "(me)" : ""}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {error && (
            <p className="text-sm text-red-600 bg-red-50 rounded-lg px-3 py-2">{error}</p>
          )}

          <div className="flex gap-2 pt-1">
            <button type="button" onClick={onClose} className="btn-secondary flex-1">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className={cn("btn-primary flex-1 justify-center", loading && "opacity-70")}
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-cream-card/30 border-t-cream-card rounded-full animate-spin" />
              ) : mode === "create" ? (
                "Create task"
              ) : (
                "Save changes"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
