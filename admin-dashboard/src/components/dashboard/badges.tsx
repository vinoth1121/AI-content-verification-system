"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { CheckCircle2, AlertTriangle, XCircle, Clock } from "lucide-react";
import { ScanOut } from "@/lib/api/acvs";

const labelConfig: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; icon: typeof CheckCircle2; className: string }> = {
  human: { variant: "default", icon: CheckCircle2, className: "bg-emerald-500/15 text-emerald-700 hover:bg-emerald-500/15 border-emerald-500/20" },
  authentic: { variant: "default", icon: CheckCircle2, className: "bg-emerald-500/15 text-emerald-700 hover:bg-emerald-500/15 border-emerald-500/20" },
  ai_generated: { variant: "default", icon: AlertTriangle, className: "bg-amber-500/15 text-amber-700 hover:bg-amber-500/15 border-amber-500/20" },
  suspicious: { variant: "default", icon: AlertTriangle, className: "bg-amber-500/15 text-amber-700 hover:bg-amber-500/15 border-amber-500/20" },
  deepfake: { variant: "default", icon: XCircle, className: "bg-rose-500/15 text-rose-700 hover:bg-rose-500/15 border-rose-500/20" },
};

const statusConfig: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; icon: typeof CheckCircle2; className: string }> = {
  completed: { variant: "default", icon: CheckCircle2, className: "bg-emerald-500/15 text-emerald-700" },
  pending: { variant: "secondary", icon: Clock, className: "bg-slate-500/15 text-slate-700" },
  failed: { variant: "destructive", icon: XCircle, className: "bg-rose-500/15 text-rose-700" },
};

export function LabelBadge({ label }: { label: string | null }) {
  if (!label) return <Badge variant="outline">—</Badge>;
  const cfg = labelConfig[label] ?? labelConfig.suspicious;
  const Icon = cfg.icon;
  return (
    <Badge variant="outline" className={cn("gap-1 border", cfg.className)}>
      <Icon className="h-3 w-3" />
      {label.replace("_", " ")}
    </Badge>
  );
}

export function StatusBadge({ status }: { status: string }) {
  const cfg = statusConfig[status] ?? statusConfig.pending;
  const Icon = cfg.icon;
  return (
    <Badge variant="outline" className={cn("gap-1 border capitalize", cfg.className)}>
      <Icon className="h-3 w-3" />
      {status}
    </Badge>
  );
}

export function ModalityBadge({ modality }: { modality: ScanOut["modality"] }) {
  const map: Record<ScanOut["modality"], string> = {
    text: "Text",
    image: "Image",
    audio: "Audio",
    video: "Video",
    fake_news: "Fake News",
  };
  return <Badge variant="outline" className="capitalize">{map[modality] ?? modality}</Badge>;
}
