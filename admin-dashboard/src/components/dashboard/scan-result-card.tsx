"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ScanOut } from "@/lib/api/acvs";
import { LabelBadge, ModalityBadge, StatusBadge } from "./badges";
import { formatDistanceToNow } from "date-fns";
import { Gauge, ListChecks, MessageSquareText } from "lucide-react";

export function ScanResultCard({ scan }: { scan: ScanOut }) {
  const confidencePct = Math.round((scan.confidence ?? 0) * 100);
  const tone =
    scan.label === "deepfake"
      ? "rose"
      : scan.label === "ai_generated" || scan.label === "suspicious"
        ? "amber"
        : "emerald";

  const toneClasses: Record<string, string> = {
    rose: "text-rose-600",
    amber: "text-amber-600",
    emerald: "text-emerald-600",
  };

  return (
    <Card className="border-l-4" data-tone={tone} style={{ borderLeftColor: tone === "rose" ? "#f43f5e" : tone === "amber" ? "#f59e0b" : "#10b981" }}>
      <CardHeader className="space-y-1">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle className="text-base">Detection result</CardTitle>
          <div className="flex gap-1.5">
            <ModalityBadge modality={scan.modality} />
            <StatusBadge status={scan.status} />
            <LabelBadge label={scan.label} />
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          Scan #{scan.id} · completed {scan.completed_at ? formatDistanceToNow(new Date(scan.completed_at), { addSuffix: true }) : "—"} · {scan.duration_ms ?? 0} ms
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2 text-muted-foreground">
              <Gauge className="h-4 w-4" /> Confidence
            </span>
            <span className={`font-medium ${toneClasses[tone]}`}>{confidencePct}%</span>
          </div>
          <Progress value={confidencePct} className="h-2" />
        </div>

        {scan.explanation && (
          <div className="space-y-1">
            <p className="flex items-center gap-2 text-sm font-medium">
              <MessageSquareText className="h-4 w-4 text-muted-foreground" /> Explanation
            </p>
            <p className="text-sm text-muted-foreground leading-relaxed">{scan.explanation}</p>
          </div>
        )}

        {scan.result?.features && Object.keys(scan.result.features).length > 0 && (
          <>
            <Separator />
            <div className="space-y-2">
              <p className="flex items-center gap-2 text-sm font-medium">
                <ListChecks className="h-4 w-4 text-muted-foreground" /> Detected features
              </p>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {Object.entries(scan.result.features).map(([k, v]) => (
                  <div
                    key={k}
                    className="rounded-md border bg-muted/30 px-2.5 py-1.5 text-xs"
                  >
                    <div className="text-muted-foreground capitalize">{k.replace(/_/g, " ")}</div>
                    <div className="font-medium">
                      {typeof v === "number" ? (Number.isInteger(v) ? v : v.toFixed(4)) : String(v)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {scan.result?.flagged_segments && scan.result.flagged_segments.length > 0 && (
          <>
            <Separator />
            <div className="space-y-2">
              <p className="text-sm font-medium">Flagged segments</p>
              <div className="max-h-40 overflow-y-auto space-y-1 rounded-md border bg-muted/20 p-2">
                {scan.result.flagged_segments.map((seg: any, i: number) => (
                  <div key={i} className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">Segment #{seg.frame_index ?? i + 1}</span>
                    <div className="flex items-center gap-2">
                      <LabelBadge label={seg.label} />
                      <span className="font-medium">{Math.round((seg.confidence ?? 0) * 100)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
