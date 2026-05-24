"use client";

import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import { initials } from "@/lib/utils";
import { LogOut, LayoutDashboard } from "lucide-react";

export function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="sticky top-0 z-40 bg-cream/90 backdrop-blur-sm border-b border-ink/8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-2">
          <LayoutDashboard className="w-4 h-4 text-accent" />
          <span className="font-display text-lg text-ink">
            Task<span className="text-accent">Flow</span>
          </span>
        </Link>

        {user && (
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex flex-col items-end">
              <span className="text-sm font-medium text-ink leading-tight">
                {user.name || user.email}
              </span>
              <span className="text-xs text-ink-faint">{user.email}</span>
            </div>

            {/* Avatar */}
            <div className="w-8 h-8 rounded-full overflow-hidden bg-ink flex items-center justify-center shrink-0">
              {user.avatar_url ? (
                <Image
                  src={user.avatar_url}
                  alt={user.name || user.email}
                  width={32}
                  height={32}
                  className="object-cover"
                />
              ) : (
                <span className="text-xs font-semibold text-cream-card">
                  {initials(user.name, user.email)}
                </span>
              )}
            </div>

            <button
              onClick={logout}
              className="btn-ghost p-2 text-ink-faint hover:text-ink"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
