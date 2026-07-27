"use client";

import { useState } from "react";
import { Loader2, Upload, ImageIcon, Mic, Video } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, ScanOut } from "@/lib/api/acvs";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ScanResultCard } from "./scan-result-card";

function FileDrop({
  accept,
  onFile,
  label,
  icon: Icon,
}: {
  accept: string;
  onFile: (f: File) => void;
  label: string;
  icon: typeof ImageIcon;
}) {
  const [fileName, setFileName] = useState<string | null>(null);
  return (
    <div className="space-y-3">
      <Label>{label}</Label>
      <label
        className="flex flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-muted-foreground/40 bg-muted/20 p-8 text-center cursor-pointer hover:bg-muted/40 transition"
      >
        <Icon className="h-8 w-8 text-muted-foreground" />
        <span className="text-sm font-medium">
          {fileName ? fileName : "Click to upload or drag and drop"}
        </span>
        <span className="text-xs text-muted-foreground">{accept}</span>
        <input
          type="file"
          accept={accept}
          className="hidden"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) {
              setFileName(f.name);
              onFile(f);
            }
          }}
        />
      </label>
    </div>
  );
}

export function FileScanPanel({ onScanComplete }: { onScanComplete?: () => void }) {
  const [result, setResult] = useState<ScanOut | null>(null);
  const [pendingFile, setPendingFile] = useState<File | null>(null);
  const [activeTab, setActiveTab] = useState("image");

  const mutation = useMutation({
    mutationFn: async (params: { file: File; tab: string }) => {
      if (params.tab === "image") return api.scanImage(params.file);
      if (params.tab === "audio") return api.scanAudio(params.file);
      if (params.tab === "video") return api.scanVideo(params.file);
      throw new Error("Unknown tab");
    },
    onSuccess: (data) => {
      setResult(data);
      toast.success("Detection complete");
      onScanComplete?.();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="space-y-4">
      <Tabs
        value={activeTab}
        onValueChange={(t) => {
          setActiveTab(t);
          setPendingFile(null);
        }}
      >
        <TabsList>
          <TabsTrigger value="image" className="gap-2">
            <ImageIcon className="h-4 w-4" /> Image
          </TabsTrigger>
          <TabsTrigger value="audio" className="gap-2">
            <Mic className="h-4 w-4" /> Audio
          </TabsTrigger>
          <TabsTrigger value="video" className="gap-2">
            <Video className="h-4 w-4" /> Video
          </TabsTrigger>
        </TabsList>

        <TabsContent value="image" className="mt-4">
          <FileDrop
            accept="PNG, JPEG, WEBP (max 10 MB)"
            onFile={setPendingFile}
            label="Image to verify"
            icon={ImageIcon}
          />
        </TabsContent>
        <TabsContent value="audio" className="mt-4">
          <FileDrop
            accept="WAV, MP3, FLAC (max 50 MB)"
            onFile={setPendingFile}
            label="Audio to verify"
            icon={Mic}
          />
        </TabsContent>
        <TabsContent value="video" className="mt-4">
          <FileDrop
            accept="MP4, WEBM (max 100 MB)"
            onFile={setPendingFile}
            label="Video to verify"
            icon={Video}
          />
        </TabsContent>
      </Tabs>

      <Button
        onClick={() => pendingFile && mutation.mutate({ file: pendingFile, tab: activeTab })}
        disabled={!pendingFile || mutation.isPending}
      >
        {mutation.isPending ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <Upload className="mr-2 h-4 w-4" />
        )}
        Run detection
      </Button>

      {result && <ScanResultCard scan={result} />}
    </div>
  );
}
