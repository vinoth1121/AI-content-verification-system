"use client";

import { useState } from "react";
import { Loader2, Send, FileText, Newspaper } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { api, ScanOut } from "@/lib/api/acvs";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { ScanResultCard } from "./scan-result-card";

const SAMPLE_TEXTS = [
  {
    label: "Human sample",
    text: "I went to the store yesterday. They were out of milk. Got eggs instead. Walked home in the rain.",
  },
  {
    label: "AI-like sample",
    text: "It is important to note that this system represents a comprehensive approach to addressing the multifaceted challenges inherent in modern content verification. Furthermore, the implementation of said framework necessitates a thorough understanding of the underlying methodologies and their respective implications.",
  },
  {
    label: "Clickbait sample",
    text: "SHOCKING: Doctors HATE this one trick for losing weight! You won't believe what happens next. The secret the medical industry doesn't want you to know!",
  },
];

export function TextScanPanel({ onScanComplete }: { onScanComplete?: () => void }) {
  const [text, setText] = useState("");
  const [title, setTitle] = useState("");
  const [result, setResult] = useState<ScanOut | null>(null);

  const textMutation = useMutation({
    mutationFn: (txt: string) => api.scanText(txt),
    onSuccess: (data) => {
      setResult(data);
      toast.success("Text scan complete");
      onScanComplete?.();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  const fakeNewsMutation = useMutation({
    mutationFn: ({ txt, ttl }: { txt: string; ttl?: string }) => api.scanFakeNews(txt, ttl),
    onSuccess: (data) => {
      setResult(data);
      toast.success("Fake-news analysis complete");
      onScanComplete?.();
    },
    onError: (e: Error) => toast.error(e.message),
  });

  return (
    <div className="space-y-4">
      <Tabs defaultValue="text">
        <TabsList>
          <TabsTrigger value="text" className="gap-2">
            <FileText className="h-4 w-4" /> AI Text Detection
          </TabsTrigger>
          <TabsTrigger value="fake-news" className="gap-2">
            <Newspaper className="h-4 w-4" /> Fake News Detection
          </TabsTrigger>
        </TabsList>

        <TabsContent value="text" className="space-y-3 mt-4">
          <div className="space-y-2">
            <Label>Text to analyse</Label>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={6}
              placeholder="Paste the text you want to verify…"
              className="resize-y"
            />
            <p className="text-xs text-muted-foreground">{text.length} / 50,000 chars</p>
          </div>

          <div className="flex flex-wrap gap-2">
            {SAMPLE_TEXTS.map((s) => (
              <Button
                key={s.label}
                size="sm"
                variant="outline"
                onClick={() => setText(s.text)}
                type="button"
              >
                {s.label}
              </Button>
            ))}
          </div>

          <Button
            onClick={() => textMutation.mutate(text)}
            disabled={!text.trim() || textMutation.isPending}
          >
            {textMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Send className="mr-2 h-4 w-4" />
            )}
            Detect AI-generated text
          </Button>
        </TabsContent>

        <TabsContent value="fake-news" className="space-y-3 mt-4">
          <div className="space-y-2">
            <Label>Headline (optional)</Label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Article headline…"
            />
          </div>
          <div className="space-y-2">
            <Label>Article body</Label>
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={6}
              placeholder="Paste the full article body…"
              className="resize-y"
            />
          </div>
          <Button
            onClick={() => fakeNewsMutation.mutate({ txt: text, ttl: title })}
            disabled={!text.trim() || fakeNewsMutation.isPending}
          >
            {fakeNewsMutation.isPending ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Newspaper className="mr-2 h-4 w-4" />
            )}
            Analyse for misinformation
          </Button>
        </TabsContent>
      </Tabs>

      {result && <ScanResultCard scan={result} />}
    </div>
  );
}
