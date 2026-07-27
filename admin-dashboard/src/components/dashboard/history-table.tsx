"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, ScanOut } from "@/lib/api/acvs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { LabelBadge, ModalityBadge, StatusBadge } from "./badges";
import { formatDistanceToNow } from "date-fns";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { ScanResultCard } from "./scan-result-card";

export function HistoryTable() {
  const [page, setPage] = useState(1);
  const [modality, setModality] = useState<string>("all");
  const [selected, setSelected] = useState<ScanOut | null>(null);

  const { data, isLoading, isFetching, refetch } = useQuery({
    queryKey: ["history", page, modality],
    queryFn: () =>
      api.history({
        page,
        page_size: 10,
        modality: modality === "all" ? undefined : modality,
      }),
  });

  const totalPages = data ? Math.max(1, Math.ceil(data.total / data.page_size)) : 1;

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Filter:</span>
          <Select value={modality} onValueChange={(v) => { setModality(v); setPage(1); }}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Modality" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All modalities</SelectItem>
              <SelectItem value="text">Text</SelectItem>
              <SelectItem value="image">Image</SelectItem>
              <SelectItem value="audio">Audio</SelectItem>
              <SelectItem value="video">Video</SelectItem>
              <SelectItem value="fake_news">Fake News</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <p className="text-xs text-muted-foreground">
          {data ? `${data.total} total` : "—"}
        </p>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-16">#</TableHead>
              <TableHead>Modality</TableHead>
              <TableHead>Label</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>When</TableHead>
              <TableHead className="w-16"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell colSpan={7}>
                    <Skeleton className="h-8 w-full" />
                  </TableCell>
                </TableRow>
              ))
            ) : data && data.items.length > 0 ? (
              data.items.map((s) => (
                <TableRow
                  key={s.id}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => setSelected(s)}
                >
                  <TableCell className="font-mono text-xs">{s.id}</TableCell>
                  <TableCell><ModalityBadge modality={s.modality} /></TableCell>
                  <TableCell><LabelBadge label={s.label} /></TableCell>
                  <TableCell>
                    {s.confidence != null ? `${Math.round(s.confidence * 100)}%` : "—"}
                  </TableCell>
                  <TableCell><StatusBadge status={s.status} /></TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(s.created_at), { addSuffix: true })}
                  </TableCell>
                  <TableCell>
                    {s.status === "completed" && (
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setSelected(s); }}>
                        View
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-sm text-muted-foreground py-8">
                  No scans yet. Run your first scan from the “New scan” tab.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page === 1 || isFetching}
        >
          <ChevronLeft className="h-4 w-4" /> Prev
        </Button>
        <span className="text-xs text-muted-foreground">
          Page {page} of {totalPages}
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page === totalPages || isFetching}
        >
          Next <ChevronRight className="h-4 w-4" />
        </Button>
      </div>

      {selected && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-muted-foreground">Selected scan</h3>
          <ScanResultCard scan={selected} />
        </div>
      )}
    </div>
  );
}
