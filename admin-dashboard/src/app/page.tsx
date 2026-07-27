"use client";

import { useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import { AuthCard } from "@/components/dashboard/auth-card";
import { DashboardShell } from "@/components/dashboard/dashboard-shell";
import { clearSession, getStoredUser, getAccessToken, User } from "@/lib/api/acvs";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1, refetchOnWindowFocus: false },
  },
});

// Restore session at module load (client-only).
function readInitialUser(): User | null {
  if (typeof window === "undefined") return null;
  const stored = getStoredUser();
  const token = getAccessToken();
  return stored && token ? stored : null;
}

export default function Page() {
  // Lazy initialiser — runs once on the client, never in an effect.
  const [user, setUser] = useState<User | null>(readInitialUser);

  return (
    <QueryClientProvider client={queryClient}>
      <Toaster richColors position="top-right" />
      {user ? (
        <DashboardShell
          user={user}
          onLogout={() => {
            clearSession();
            setUser(null);
          }}
        />
      ) : (
        <AuthCard onAuthed={() => setUser(getStoredUser())} />
      )}
    </QueryClientProvider>
  );
}
