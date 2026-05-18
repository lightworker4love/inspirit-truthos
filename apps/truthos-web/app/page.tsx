"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function WelcomePage() {
  const router = useRouter();
  const [userId, setUserId] = useState("");
  const [openingPrompt, setOpeningPrompt] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    queueMicrotask(() => {
      const params = new URLSearchParams(window.location.search);
      if (params.get("reason") === "missing-user") {
        setNotice("請先告訴我你的名字");
      }
      setUserId(sessionStorage.getItem("truthos_user_id") || "");
    });
  }, []);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedUserId = userId.trim();
    if (!trimmedUserId) {
      setError("請輸入你的名字或代號，讓我知道該如何稱呼你");
      return;
    }

    setError("");
    setLoading(true);
    sessionStorage.setItem("truthos_user_id", trimmedUserId);

    const prompt = openingPrompt.trim();
    const target = prompt ? `/chat?prompt=${encodeURIComponent(prompt)}` : "/chat";
    router.push(target);
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-8rem)] w-full max-w-xl flex-col justify-center px-6 py-12">
      <div className="mb-10 space-y-5">
        <p className="text-sm tracking-[0.18em] text-muted-foreground uppercase">
          iN SPiRiT Life Blueprint
        </p>
        <h1 className="font-serif text-5xl leading-tight text-balance md:text-6xl">
          你好，我是 Hermes
        </h1>
        <p className="max-w-lg text-lg leading-8 text-muted-foreground">
          這裡是一個私密的反思空間，讓我們一起看見你生命藍圖的輪廓。
        </p>
      </div>

      <Card className="border-border/80 bg-surface/90 shadow-sm">
        <CardContent className="p-6">
          <form className="space-y-5" onSubmit={submit}>
            {notice ? (
              <div className="rounded-lg border border-primary/30 bg-primary/10 px-4 py-3 text-sm text-primary">
                {notice}
              </div>
            ) : null}

            <label className="block space-y-2">
              <span className="text-sm text-muted-foreground">名字或代號</span>
              <Input
                value={userId}
                onChange={(event) => setUserId(event.target.value)}
                placeholder="你希望我怎麼稱呼你？"
                aria-invalid={Boolean(error)}
              />
            </label>

            <label className="block space-y-2">
              <span className="text-sm text-muted-foreground">
                今天帶你來這裡的，是什麼？（可略過）
              </span>
              <Textarea
                value={openingPrompt}
                onChange={(event) => setOpeningPrompt(event.target.value)}
                placeholder="你可以簡短寫下現在最想被理解的一件事"
                rows={4}
              />
            </label>

            {error ? <p className="text-sm text-destructive">{error}</p> : null}

            <Button
              className="h-11 w-full bg-primary text-primary-foreground hover:bg-primary/90"
              disabled={loading}
              type="submit"
            >
              {loading ? "正在進入..." : "開始對話"}
              <ArrowRight aria-hidden="true" />
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
