"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

function AuthCallbackContent() {
  const { setToken } = useAuth();
  const router = useRouter();
  const params = useSearchParams();

  useEffect(() => {
    const token = params.get("token");

    if (token) {
      setToken(token);
      router.replace("/dashboard");
    } else {
      router.replace("/login");
    }
  }, [params, setToken, router]);

  return (
    <div className="min-h-screen bg-cream flex flex-col items-center justify-center gap-4">
      <div className="w-8 h-8 border-2 border-ink/20 border-t-ink rounded-full animate-spin" />
      <p className="text-sm text-ink-muted">Signing you in…</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-cream flex items-center justify-center">
          Loading...
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  );
}
