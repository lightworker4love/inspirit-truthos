"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { ArrowRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ApiError, getSoulMap, SoulMapResponse } from "@/lib/api";
import { parsePattern } from "@/lib/patterns";

function formatDate(value?: string | null) {
  if (!value) {
    return "剛剛建立";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "剛剛建立";
  }

  return new Intl.DateTimeFormat("zh-TW", {
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(date);
}

function getPrimaryPattern(map: SoulMapResponse) {
  const patterns = map.recurring_patterns || [];
  const weights = map.pattern_weights || {};
  if (!patterns.length) {
    return undefined;
  }

  return [...patterns].sort((a, b) => {
    const aWeight = weights[a.id || ""]?.weight || 0;
    const bWeight = weights[b.id || ""]?.weight || 0;
    return bWeight - aWeight;
  })[0];
}

function LoadingState({ warming }: { warming: boolean }) {
  return (
    <section className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-8 space-y-3">
        <Skeleton className="h-8 w-52" />
        <Skeleton className="h-5 w-96 max-w-full" />
        {warming ? (
          <p className="text-sm text-muted-foreground">
            靈魂藍圖載入中，正在連線...
          </p>
        ) : null}
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        {[0, 1, 2, 3].map((item) => (
          <Skeleton className="h-44" key={item} />
        ))}
      </div>
    </section>
  );
}

function EmptyState() {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-8rem)] max-w-xl flex-col justify-center px-6 py-12">
      <Card className="border-border bg-surface">
        <CardContent className="space-y-5 p-8">
          <div className="flex size-12 items-center justify-center rounded-full border border-primary/30 text-primary">
            ○
          </div>
          <div className="space-y-3">
            <h1 className="font-serif text-4xl">你的靈魂藍圖正在成形</h1>
            <p className="text-lg leading-8 text-muted-foreground">
              開始對話後，這裡會逐漸浮現你的生命模式。
            </p>
          </div>
          <Link
            className="inline-flex h-11 w-fit items-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            href="/chat"
          >
            開始第一次對話 <ArrowRight aria-hidden="true" className="size-4" />
          </Link>
        </CardContent>
      </Card>
    </section>
  );
}

function InsightCard({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <Card className="border-border bg-surface">
      <CardHeader>
        <CardDescription>{label}</CardDescription>
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}

export default function SoulMapPage() {
  const [map, setMap] = useState<SoulMapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [warming, setWarming] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let warmupTimer: number | undefined;

    queueMicrotask(() => {
      const userId = sessionStorage.getItem("truthos_user_id");
      if (!userId) {
        setLoading(false);
        setError("請先回到首頁，告訴 Hermes 該如何稱呼你。");
        return;
      }

      warmupTimer = window.setTimeout(() => {
        setWarming(true);
      }, 5_000);

      getSoulMap(userId)
        .then(setMap)
        .catch((caught) => {
          if (caught instanceof ApiError && caught.status === 404) {
            setMap({
              user_id: userId,
              status: "not_yet_built",
            });
          } else {
            setError("靈魂藍圖暫時無法載入，請稍候再試。");
          }
        })
        .finally(() => {
          if (warmupTimer) {
            window.clearTimeout(warmupTimer);
          }
          setLoading(false);
          setWarming(false);
        });
    });

    return () => {
      if (warmupTimer) {
        window.clearTimeout(warmupTimer);
      }
    };
  }, []);

  const primaryPattern = useMemo(() => (map ? getPrimaryPattern(map) : undefined), [map]);
  const primaryPatternId = primaryPattern?.id;
  const parsedPattern = primaryPatternId ? parsePattern(primaryPatternId) : undefined;
  const frequency = primaryPatternId
    ? map?.pattern_weights?.[primaryPatternId]?.frequency || 0
    : 0;
  const frequencyDots = Math.min(Math.max(frequency, 0), 8);
  const status = map?.status || "active";

  if (loading) {
    return <LoadingState warming={warming} />;
  }

  if (error) {
    return (
      <section className="mx-auto max-w-xl px-6 py-12">
        <Card className="border-destructive/30 bg-surface">
          <CardContent className="space-y-4 p-6">
            <h1 className="font-serif text-3xl">暫時無法讀取</h1>
            <p className="text-muted-foreground">{error}</p>
            <Link
              className="inline-flex h-10 w-fit items-center rounded-lg border border-border px-4 text-sm font-medium hover:bg-muted"
              href="/"
            >
              回到首頁
            </Link>
          </CardContent>
        </Card>
      </section>
    );
  }

  if (!map || map.status === "not_yet_built") {
    return <EmptyState />;
  }

  return (
    <section className="mx-auto max-w-5xl px-6 py-10">
      <div className="mb-9 max-w-2xl space-y-3">
        <p className="text-sm tracking-[0.16em] text-muted-foreground uppercase">
          Soul Map
        </p>
        <h1 className="font-serif text-5xl leading-tight">靈魂藍圖</h1>
        <p className="text-lg leading-8 text-muted-foreground">
          這裡不是診斷，而是你在對話中逐漸浮現的生命模式。
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <InsightCard label="當前狀態">
          <Badge className="h-7 rounded-full bg-emerald-700 px-3 text-sm text-white">
            {status}
          </Badge>
        </InsightCard>

        <InsightCard label="核心模式">
          {parsedPattern ? (
            <div className="space-y-3">
              <CardTitle className="text-2xl">{parsedPattern.label}</CardTitle>
              <p className="text-base leading-7 text-muted-foreground">
                {parsedPattern.description}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <CardTitle className="text-2xl text-muted-foreground">
                模式尚未確立
              </CardTitle>
              <p className="text-base leading-7 text-muted-foreground">
                再多一點真實對話後，這裡會慢慢浮現更清楚的生命模式。
              </p>
            </div>
          )}
        </InsightCard>

        <InsightCard label="出現頻率">
          <div className="space-y-4">
            <p className="text-2xl font-medium">
              {frequency > 0 ? `${frequency} 次對話` : "首次記錄"}
            </p>
            <div className="flex gap-2">
              {Array.from({ length: 8 }).map((_, index) => (
                <span
                  className={
                    index < frequencyDots
                      ? "h-2 flex-1 rounded-full bg-primary"
                      : "h-2 flex-1 rounded-full bg-muted"
                  }
                  key={index}
                />
              ))}
            </div>
          </div>
        </InsightCard>

        <InsightCard label="最後更新">
          <p className="text-2xl font-medium">{formatDate(map.updated_at)}</p>
          <p className="mt-3 text-sm text-muted-foreground">
            生命模式會隨著新的對話逐步更新。
          </p>
        </InsightCard>
      </div>
    </section>
  );
}
