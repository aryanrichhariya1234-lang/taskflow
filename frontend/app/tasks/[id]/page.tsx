"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter, useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";
import { Task, User } from "@/types";
import { apiGet, apiPatch, apiDelete } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import { TaskForm } from "@/components/TaskForm";
import {
  cn, priorityConfig, statusConfig, formatDueDate, isDueSoon, initials
} from "@/lib/utils";
import { ArrowLeft, Calendar, Edit2, Trash2, User2 } from "lucide-react";

export default function TaskDetailPage() {
  const { user, token, loading } = useAuth();
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const id = params.id;

  const [task, setTask] = useState<Task | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [fetching, setFetching] = useState(true);
  const [editing, setEditing] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [user, loading, router]);

  const fetchTask = useCallback(async () => {
    if (!token || !id) return;
    setFetching(true);
    try {
      const [t, u] = await Promise.all([
        apiGet<Task>(`/tasks/${id}`, token),
        apiGet<User[]>("/users", token),
      ]);
      setTask(t);
      setUsers(u);
    } catch {
      router.replace("/dashboard");
    } finally {
      setFetching(false);
    }
  }, [token, id, router]);

  useEffect(() => { fetchTask(); }, [fetchTask]);

  const handleUpdate = async (data: Partial<Task>) => {
    await apiPatch<Task>(`/tasks/${id}`, data, token);
    await fetchTask();
  };

  const handleDelete = async () => {
    if (!confirm("Delete this task? This cannot be undone.")) return;
    setDeleting(true);
    try {
      await apiDelete(`/tasks/${id}`, token);
      router.replace("/dashboard");
    } finally {
      setDeleting(false);
    }
  };

  const handleStatusChange = async (status: Task["status"]) => {
    setTask((prev) => prev ? { ...prev, status } : prev);
    await apiPatch(`/tasks/${id}`, { status }, token);
  };

  if (loading || fetching || !task) {
    return (
      <div className="min-h-screen bg-cream flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-ink/20 border-t-ink rounded-full animate-spin" />
      </div>
    );
  }

  const priority = priorityConfig[task.priority];
  const status = statusConfig[task.status];
  const isCreator = task.creator_id === user?.id;
  const overdue = isDueSoon(task.due_date) && task.status !== "done";

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8 animate-fade-in">
        {/* Back */}
        <Link href="/dashboard" className="btn-ghost mb-6 inline-flex">
          <ArrowLeft className="w-4 h-4" />
          Back to board
        </Link>

        <div className="card p-6 sm:p-8 space-y-6">
          {/* Top row */}
          <div className="flex items-start justify-between gap-4">
            <h1 className="font-display text-2xl text-ink leading-snug">{task.title}</h1>
            {isCreator && (
              <div className="flex gap-2 shrink-0">
                <button onClick={() => setEditing(true)} className="btn-ghost p-2">
                  <Edit2 className="w-4 h-4" />
                </button>
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="btn-ghost p-2 text-red-500 hover:text-red-600"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>

          {/* Meta badges */}
          <div className="flex flex-wrap gap-2">
            <span className={cn("badge", priority.color)}>{priority.label} priority</span>

            {/* Status cycle */}
            <button
              onClick={() => {
                const next: Task["status"][] = ["todo", "in_progress", "done"];
                const idx = next.indexOf(task.status);
                handleStatusChange(next[(idx + 1) % 3]);
              }}
              className={cn(
                "badge cursor-pointer hover:opacity-80 transition-opacity",
                status.color
              )}
            >
              <span className={cn("w-1.5 h-1.5 rounded-full", status.dot)} />
              {status.label}
            </button>

            {task.due_date && (
              <span
                className={cn(
                  "badge",
                  overdue
                    ? "border-red-200 bg-red-50 text-red-600"
                    : "border-ink/10 bg-cream-warm text-ink-muted"
                )}
              >
                <Calendar className="w-3 h-3" />
                {formatDueDate(task.due_date)}
                {overdue && " — overdue"}
              </span>
            )}
          </div>

          {/* Description */}
          {task.description ? (
            <p className="text-ink-soft text-sm leading-relaxed whitespace-pre-wrap">
              {task.description}
            </p>
          ) : (
            <p className="text-ink-faint text-sm italic">No description</p>
          )}

          {/* People */}
          <div className="grid sm:grid-cols-2 gap-4 pt-2 border-t border-ink/8">
            <PersonField label="Created by" user={task.creator} />
            <PersonField label="Assigned to" user={task.assignee} />
          </div>

          {/* Timestamps */}
          <div className="text-xs text-ink-faint flex gap-4 pt-2 border-t border-ink/8">
            <span>Created {new Date(task.created_at).toLocaleDateString()}</span>
            <span>Updated {new Date(task.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
      </main>

      {editing && (
        <TaskForm
          mode="edit"
          initial={task}
          users={users}
          currentUserId={user?.id ?? ""}
          onSubmit={handleUpdate}
          onClose={() => setEditing(false)}
        />
      )}
    </div>
  );
}

function PersonField({ label, user }: { label: string; user: User | null }) {
  return (
    <div>
      <p className="text-xs font-medium text-ink-faint uppercase tracking-wide mb-2">{label}</p>
      {user ? (
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full overflow-hidden bg-ink flex items-center justify-center shrink-0">
            {user.avatar_url ? (
              <Image
                src={user.avatar_url}
                alt={user.name || user.email}
                width={28}
                height={28}
                className="object-cover"
              />
            ) : (
              <span className="text-[10px] font-semibold text-cream-card">
                {initials(user.name, user.email)}
              </span>
            )}
          </div>
          <div>
            <p className="text-sm font-medium text-ink leading-tight">{user.name || "—"}</p>
            <p className="text-xs text-ink-faint">{user.email}</p>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-ink-faint">
          <User2 className="w-4 h-4" />
          <span className="text-sm">Unassigned</span>
        </div>
      )}
    </div>
  );
}
