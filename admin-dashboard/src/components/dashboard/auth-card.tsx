"use client";

import { useMemo, useState } from "react";
import { Eye, EyeOff, Loader2, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { useMutation } from "@tanstack/react-query";
import { api, setSession } from "@/lib/api/acvs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";

interface Props {
  onAuthed: () => void;
}

export function AuthCard({ onAuthed }: Props) {
  const [email, setEmail] = useState("admin@acvs.io");
  const [password, setPassword] = useState("Admin123!Admin");
  const [showPw, setShowPw] = useState(false);
  const [mode, setMode] = useState<"login" | "register">("login");
  const [fullName, setFullName] = useState("");

  const mutation = useMutation({
    mutationFn: async () => {
      if (mode === "login") return api.login(email, password);
      return api.register(email, fullName, password);
    },
    onSuccess: (data) => {
      setSession(data.access_token, data.refresh_token, data.user);
      toast.success(`Welcome, ${data.user.full_name}`);
      onAuthed();
    },
    onError: (err: Error) => {
      toast.error(err.message || "Authentication failed");
    },
  });

  const canSubmit = useMemo(() => {
    if (!email || !password) return false;
    if (mode === "register" && !fullName) return false;
    return true;
  }, [email, password, fullName, mode]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background via-background to-muted/30 p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="space-y-2 text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10">
            <ShieldCheck className="h-6 w-6 text-emerald-600" />
          </div>
          <CardTitle className="text-2xl">AI Content Verification</CardTitle>
          <CardDescription>
            Sign in to scan content for AI-generation, deepfakes, and misinformation.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Tabs
            value={mode}
            onValueChange={(v) => setMode(v as "login" | "register")}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Sign in</TabsTrigger>
              <TabsTrigger value="register">Create account</TabsTrigger>
            </TabsList>

            <TabsContent value="login" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  autoComplete="email"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPw ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    autoComplete="current-password"
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3"
                    onClick={() => setShowPw((s) => !s)}
                  >
                    {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </TabsContent>

            <TabsContent value="register" className="space-y-4 mt-4">
              <div className="space-y-2">
                <Label htmlFor="fullName">Full name</Label>
                <Input
                  id="fullName"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Ada Lovelace"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email-r">Email</Label>
                <Input
                  id="email-r"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password-r">Password</Label>
                <Input
                  id="password-r"
                  type={showPw ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="At least 8 characters"
                />
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>

        <CardFooter className="flex flex-col gap-3">
          <Button
            className="w-full"
            disabled={!canSubmit || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {mutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {mode === "login" ? "Sign in" : "Create account"}
          </Button>
          <p className="text-xs text-muted-foreground text-center">
            Demo: admin@acvs.io / Admin123!Admin &nbsp;·&nbsp; user@acvs.io / User123!User
          </p>
        </CardFooter>
      </Card>
    </div>
  );
}
