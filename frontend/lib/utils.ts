import { type ClassValue, clsx } from "clsx";
import { format, isToday, isTomorrow, isPast } from "date-fns";
import { TaskPriority, TaskStatus } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function formatDueDate(dateStr: string | null): string {
  if (!dateStr) return "";
  const d = new Date(dateStr + "T00:00:00");
  if (isToday(d)) return "Today";
  if (isTomorrow(d)) return "Tomorrow";
  return format(d, "MMM d");
}

export function isDueSoon(dateStr: string | null): boolean {
  if (!dateStr) return false;
  const d = new Date(dateStr + "T00:00:00");
  return isPast(d) || isToday(d);
}

export const priorityConfig: Record<TaskPriority, { label: string; color: string }> = {
  high: { label: "High", color: "bg-red-100 text-red-700 border-red-200" },
  medium: { label: "Medium", color: "bg-amber-100 text-amber-700 border-amber-200" },
  low: { label: "Low", color: "bg-emerald-100 text-emerald-700 border-emerald-200" },
};

export const statusConfig: Record<TaskStatus, { label: string; color: string; dot: string }> = {
  todo: { label: "To do", color: "bg-ink-faint/20 text-ink-muted", dot: "bg-ink-faint" },
  in_progress: { label: "In progress", color: "bg-blue-100 text-blue-700", dot: "bg-blue-500" },
  done: { label: "Done", color: "bg-accent-dim text-emerald-700", dot: "bg-accent" },
};

export function initials(name: string | null, email: string): string {
  if (name) {
    return name
      .split(" ")
      .map((w) => w[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  }
  return email[0].toUpperCase();
}
