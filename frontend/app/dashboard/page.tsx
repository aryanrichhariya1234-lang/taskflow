"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { Task, User, TaskStatus } from "@/types";
import { apiGet, apiPost, apiPatch } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import { TaskCard } from "@/components/TaskCard";
import { TaskForm } from "@/components/TaskForm";
import { statusConfig } from "@/lib/utils";
import { Plus, Search, SlidersHorizontal } from "lucide-react";

const COLUMNS: { id: TaskStatus; label: string }[] = [
  { id: "todo", label: "To do" },
  { id: "in_progress", label: "In progress" },
  { id: "done", label: "Done" },
];

export default function DashboardPage() {
  const { user, token, loading } = useAuth();
  const router = useRouter();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [fetching, setFetching] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [search, setSearch] = useState("");
  const [filterPriority, setFilterPriority] = useState<string>("all");

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [user, loading, router]);

  const fetchData = useCallback(async () => {
    if (!token) return;
    setFetching(true);
    try {
      const [t, u] = await Promise.all([
        apiGet<Task[]>("/tasks", token),
        apiGet<User[]>("/users", token),
      ]);
      setTasks(t);
      setUsers(u);
    } catch (e) {
      console.error(e);
    } finally {
      setFetching(false);
    }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleCreate = async (data: Parameters<typeof apiPost>[1]) => {
    await apiPost<Task>("/tasks", data, token);
    await fetchData();
  };

  const handleStatusChange = async (id: string, status: TaskStatus) => {
    setTasks((prev) => prev.map((t) => (t.id === id ? { ...t, status } : t)));
    try {
      await apiPatch(`/tasks/${id}`, { status }, token);
    } catch {
      await fetchData(); // revert on error
    }
  };

  // Filter tasks
  const filtered = tasks.filter((t) => {
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      t.title.toLowerCase().includes(q) ||
      (t.description || "").toLowerCase().includes(q);
    const matchPriority = filterPriority === "all" || t.priority === filterPriority;
    return matchSearch && matchPriority;
  });

  const byStatus = (status: TaskStatus) => filtered.filter((t) => t.status === status);

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-cream flex items-center justify-center">
        <div className="w-6 h-6 border-2 border-ink/20 border-t-ink rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 mb-8 flex-wrap">
          <div>
            <h1 className="font-display text-3xl text-ink mb-1">
              Good {getGreeting()},{" "}
              <span className="text-accent">{(user.name || user.email).split(" ")[0]}</span>
            </h1>
            <p className="text-ink-muted text-sm">
              {tasks.filter((t) => t.status !== "done").length} active tasks
            </p>
          </div>

          <button onClick={() => setShowForm(true)} className="btn-primary">
            <Plus className="w-4 h-4" />
            New task
          </button>
        </div>

        {/* Filters */}
        <div className="flex gap-3 mb-6 flex-wrap">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-ink-faint" />
            <input
              className="input pl-9"
              placeholder="Search tasks…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="flex items-center gap-2">
            <SlidersHorizontal className="w-4 h-4 text-ink-faint" />
            <select
              className="select w-auto"
              value={filterPriority}
              onChange={(e) => setFilterPriority(e.target.value)}
            >
              <option value="all">All priorities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
        </div>

        {/* Kanban columns */}
        {fetching ? (
          <div className="flex items-center justify-center h-48">
            <div className="w-6 h-6 border-2 border-ink/20 border-t-ink rounded-full animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {COLUMNS.map((col) => {
              const colTasks = byStatus(col.id);
              const cfg = statusConfig[col.id];
              return (
                <div key={col.id} className="space-y-3">
                  {/* Column header */}
                  <div className="flex items-center gap-2 px-1">
                    <span className={`w-2 h-2 rounded-full ${cfg.dot}`} />
                    <h2 className="text-sm font-semibold text-ink">{col.label}</h2>
                    <span className="ml-auto text-xs text-ink-faint font-mono bg-cream-warm rounded-full px-2 py-0.5">
                      {colTasks.length}
                    </span>
                  </div>

                  {/* Tasks */}
                  <div className="space-y-3 min-h-[80px]">
                    {colTasks.length === 0 ? (
                      <div className="h-24 rounded-xl border-2 border-dashed border-ink/10 flex items-center justify-center">
                        <span className="text-xs text-ink-faint">No tasks</span>
                      </div>
                    ) : (
                      colTasks.map((task) => (
                        <TaskCard
                          key={task.id}
                          task={task}
                          onStatusChange={handleStatusChange}
                        />
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {showForm && (
        <TaskForm
          mode="create"
          users={users}
          currentUserId={user.id}
          onSubmit={handleCreate}
          onClose={() => setShowForm(false)}
        />
      )}
    </div>
  );
}

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "morning";
  if (h < 17) return "afternoon";
  return "evening";
}
