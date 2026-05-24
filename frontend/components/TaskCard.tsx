"use client";

import Link from "next/link";
import Image from "next/image";
import { Task } from "@/types";
import { cn, priorityConfig, statusConfig, formatDueDate, isDueSoon, initials } from "@/lib/utils";
import { Calendar, User2 } from "lucide-react";

interface TaskCardProps {
  task: Task;
  onStatusChange?: (id: string, status: Task["status"]) => void;
}

export function TaskCard({ task, onStatusChange }: TaskCardProps) {
  const priority = priorityConfig[task.priority];
  const status = statusConfig[task.status];
  const overdue = isDueSoon(task.due_date) && task.status !== "done";

  return (
    <Link
      href={`/tasks/${task.id}`}
      className="card block p-4 hover:shadow-card-hover transition-all duration-200 animate-slide-up group"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="text-sm font-semibold text-ink group-hover:text-ink-soft line-clamp-2 leading-snug">
          {task.title}
        </h3>
        <span className={cn("badge shrink-0", priority.color)}>{priority.label}</span>
      </div>

      {task.description && (
        <p className="text-xs text-ink-muted line-clamp-2 mb-3 leading-relaxed">
          {task.description}
        </p>
      )}

      <div className="flex items-center justify-between gap-2 flex-wrap">
        <div className="flex items-center gap-2">
          {/* Status pill */}
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              if (onStatusChange) {
                const next: Task["status"][] = ["todo", "in_progress", "done"];
                const idx = next.indexOf(task.status);
                onStatusChange(task.id, next[(idx + 1) % 3]);
              }
            }}
            className={cn(
              "flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium transition-all hover:opacity-80",
              status.color
            )}
          >
            <span className={cn("w-1.5 h-1.5 rounded-full", status.dot)} />
            {status.label}
          </button>

          {/* Due date */}
          {task.due_date && (
            <span
              className={cn(
                "flex items-center gap-1 text-xs",
                overdue ? "text-red-600 font-medium" : "text-ink-faint"
              )}
            >
              <Calendar className="w-3 h-3" />
              {formatDueDate(task.due_date)}
            </span>
          )}
        </div>

        {/* Assignee avatar */}
        {task.assignee ? (
          <div
            className="w-6 h-6 rounded-full overflow-hidden bg-ink flex items-center justify-center"
            title={task.assignee.name || task.assignee.email}
          >
            {task.assignee.avatar_url ? (
              <Image
                src={task.assignee.avatar_url}
                alt={task.assignee.name || task.assignee.email}
                width={24}
                height={24}
                className="object-cover"
              />
            ) : (
              <span className="text-[9px] font-semibold text-cream-card">
                {initials(task.assignee.name, task.assignee.email)}
              </span>
            )}
          </div>
        ) : (
          <User2 className="w-4 h-4 text-ink-faint" />
        )}
      </div>
    </Link>
  );
}
