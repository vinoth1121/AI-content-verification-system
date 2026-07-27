"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api, getStoredUser, clearSession, User } from "@/lib/api/acvs";
import { Button } from "@/components/ui/button";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { KpiCard } from "./kpi-card";
import { ScanModalityChart, ScanLabelChart } from "./charts";
import { TextScanPanel } from "./text-scan-panel";
import { FileScanPanel } from "./file-scan-panel";
import { HistoryTable } from "./history-table";
import { AdminUsersTable } from "./admin-users-table";
import {
  Activity,
  LayoutDashboard,
  ScanLine,
  History,
  Users,
  ShieldCheck,
  LogOut,
  Sun,
  Moon,
} from "lucide-react";
import { useTheme } from "next-themes";

interface Props {
  user: User;
  onLogout: () => void;
}

export function DashboardShell({ user, onLogout }: Props) {
  const qc = useQueryClient();
  const isAdmin = user.role === "admin";
  const { theme, setTheme } = useTheme();

  const statsQuery = useQuery({
    queryKey: ["admin-stats"],
    queryFn: api.adminStats,
    enabled: isAdmin,
    refetchInterval: 30_000,
  });

  const stats = statsQuery.data;

  return (
    <div className="min-h-screen flex flex-col bg-muted/10">
      {/* Header */}
      <header className="sticky top-0 z-30 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10">
              <ShieldCheck className="h-5 w-5 text-emerald-600" />
            </div>
            <div className="leading-tight">
              <div className="text-sm font-semibold">ACVS</div>
              <div className="text-[10px] text-muted-foreground">AI Content Verification</div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              title="Toggle theme"
            >
              <Sun className="h-4 w-4 dark:hidden" />
              <Moon className="h-4 w-4 hidden dark:block" />
            </Button>
            <div className="text-right text-xs">
              <div className="font-medium">{user.full_name}</div>
              <div className="text-muted-foreground capitalize">{user.role}</div>
            </div>
            <Button variant="ghost" size="icon" onClick={onLogout} title="Sign out">
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="container mx-auto w-full max-w-6xl flex-1 px-4 py-6">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 sm:grid-cols-4 lg:grid-cols-5">
            <TabsTrigger value="overview" className="gap-2">
              <LayoutDashboard className="h-4 w-4" /> Overview
            </TabsTrigger>
            <TabsTrigger value="scan" className="gap-2">
              <ScanLine className="h-4 w-4" /> New scan
            </TabsTrigger>
            <TabsTrigger value="history" className="gap-2">
              <History className="h-4 w-4" /> History
            </TabsTrigger>
            {isAdmin && (
              <TabsTrigger value="admin-stats" className="gap-2">
                <Activity className="h-4 w-4" /> Platform
              </TabsTrigger>
            )}
            {isAdmin && (
              <TabsTrigger value="admin-users" className="gap-2">
                <Users className="h-4 w-4" /> Users
              </TabsTrigger>
            )}
          </TabsList>

          {/* Overview */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <KpiCard
                title="Total scans"
                value={stats?.scans.total ?? 0}
                hint="Across all modalities"
                icon={ScanLine}
                accent="emerald"
              />
              <KpiCard
                title="Completed"
                value={stats?.scans.completed ?? 0}
                hint={`${stats?.scans.failed ?? 0} failed`}
                icon={Activity}
                accent="sky"
              />
              <KpiCard
                title="Deepfakes detected"
                value={stats?.scans.by_label.deepfake ?? 0}
                hint="Images / videos flagged"
                icon={ShieldCheck}
                accent="rose"
              />
              <KpiCard
                title="Registered users"
                value={stats?.users.total ?? 0}
                hint="Active & disabled"
                icon={Users}
                accent="violet"
              />
            </div>

            <div className="grid gap-4 lg:grid-cols-2">
              <ScanModalityChart stats={stats} />
              <ScanLabelChart stats={stats} />
            </div>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Recent scans</CardTitle>
                <CardDescription>Your last 10 detection results</CardDescription>
              </CardHeader>
              <CardContent>
                <HistoryTable />
              </CardContent>
            </Card>
          </TabsContent>

          {/* New scan */}
          <TabsContent value="scan" className="space-y-6">
            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Run a new scan</CardTitle>
                  <CardDescription>
                    Detect AI-generated text, fake news, or deepfake media. Files are deleted automatically after inference.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <TextScanPanel onScanComplete={() => qc.invalidateQueries({ queryKey: ["history"] })} />
                  <FileScanPanel onScanComplete={() => qc.invalidateQueries({ queryKey: ["history"] })} />
                </CardContent>
              </Card>

              <Card className="bg-muted/20">
                <CardHeader>
                  <CardTitle className="text-base">How it works</CardTitle>
                  <CardDescription>Privacy-first by design</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-muted-foreground">
                  <p>
                    <strong className="text-foreground">1. Upload or paste.</strong> Text is processed in-memory; media files are passed to the AI engine for inference only.
                  </p>
                  <p>
                    <strong className="text-foreground">2. Feature extraction.</strong> The engine computes stylometric, frequency-domain, or spectral features depending on the modality.
                  </p>
                  <p>
                    <strong className="text-foreground">3. Explainable verdict.</strong> A confidence score and a human-readable explanation are returned — never a black-box label.
                  </p>
                  <p>
                    <strong className="text-foreground">4. Auto-cleanup.</strong> Uploaded media is removed after inference; only the verdict is persisted to your scan history.
                  </p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* History */}
          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Scan history</CardTitle>
                <CardDescription>All your previous scans, newest first</CardDescription>
              </CardHeader>
              <CardContent>
                <HistoryTable />
              </CardContent>
            </Card>
          </TabsContent>

          {/* Admin — Platform stats */}
          {isAdmin && (
            <TabsContent value="admin-stats" className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <KpiCard title="Total scans" value={stats?.scans.total ?? 0} icon={ScanLine} accent="emerald" />
                <KpiCard title="Completed" value={stats?.scans.completed ?? 0} icon={Activity} accent="sky" />
                <KpiCard title="Failed" value={stats?.scans.failed ?? 0} icon={ShieldCheck} accent="rose" />
                <KpiCard title="Users" value={stats?.users.total ?? 0} icon={Users} accent="violet" />
              </div>
              <div className="grid gap-4 lg:grid-cols-2">
                <ScanModalityChart stats={stats} />
                <ScanLabelChart stats={stats} />
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Average confidence per modality</CardTitle>
                  <CardDescription>Mean confidence of completed scans, by modality</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {stats && Object.entries(stats.scans.avg_confidence).map(([m, c]) => (
                      <div key={m} className="rounded-md border bg-muted/20 p-3">
                        <div className="text-xs text-muted-foreground capitalize">{m.replace("_", " ")}</div>
                        <div className="text-xl font-semibold">{(c * 100).toFixed(1)}%</div>
                      </div>
                    ))}
                    {stats && Object.keys(stats.scans.avg_confidence).length === 0 && (
                      <p className="text-sm text-muted-foreground">No completed scans yet.</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          )}

          {/* Admin — Users */}
          {isAdmin && (
            <TabsContent value="admin-users" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">User management</CardTitle>
                  <CardDescription>Enable / disable accounts and toggle admin role</CardDescription>
                </CardHeader>
                <CardContent>
                  <AdminUsersTable />
                </CardContent>
              </Card>
            </TabsContent>
          )}
        </Tabs>
      </main>

      <footer className="border-t bg-background py-3 mt-auto">
        <div className="container mx-auto max-w-6xl px-4 text-center text-xs text-muted-foreground">
          AI Content Verification System · Privacy-first · All inference runs server-side
        </div>
      </footer>
    </div>
  );
}
