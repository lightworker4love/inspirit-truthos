"use client";

import { KeyboardEvent, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { Send } from "lucide-react";

import { TypingIndicator } from "@/components/typing-indicator";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ApiError, getChatText, sendChat } from "@/lib/api";
import { cn } from "@/lib/utils";

type Message = {
  id: string;
  role: "user" | "hermes";
  text: string;
  createdAt: Date;
};

const suggestions = [
  "我現在面對的最大挑戰是...",
  "我想更了解我的生命模式...",
  "我感覺自己在原地打轉...",
];

function formatTime(date: Date) {
  return new Intl.DateTimeFormat("zh-TW", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export default function ChatPage() {
  const router = useRouter();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [userId, setUserId] = useState("");
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [mapUpdated, setMapUpdated] = useState(false);

  useEffect(() => {
    queueMicrotask(() => {
      const storedUserId = sessionStorage.getItem("truthos_user_id");
      if (!storedUserId) {
        router.replace("/?reason=missing-user");
        return;
      }

      setUserId(storedUserId);
      const params = new URLSearchParams(window.location.search);
      setDraft(params.get("prompt") || "");
      setLoading(false);
    });
  }, [router]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages, sending]);

  const count = useMemo(() => draft.length, [draft]);

  async function submit(text: string) {
    const message = text.trim();
    if (!message || sending || !userId) {
      return;
    }

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      text: message,
      createdAt: new Date(),
    };

    setMessages((current) => [...current, userMessage]);
    setDraft("");
    setError("");
    setMapUpdated(false);
    setSending(true);

    try {
      const response = await sendChat(userId, message);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "hermes",
          text: getChatText(response),
          createdAt: new Date(),
        },
      ]);
      setMapUpdated(Boolean(response.soul_map_updated));
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 422) {
        setError("請確認訊息格式正確");
      } else {
        setError("Hermes 暫時無法回應，請稍候再試");
      }
    } finally {
      setSending(false);
    }
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      submit(draft);
    }
  }

  if (loading) {
    return (
      <section className="mx-auto flex min-h-[calc(100vh-8rem)] max-w-3xl items-center px-6">
        <p className="text-muted-foreground">正在準備對話空間...</p>
      </section>
    );
  }

  return (
    <section className="mx-auto flex h-[calc(100vh-4.5rem)] max-w-4xl flex-col px-4 md:px-8">
      <div className="flex-1 overflow-y-auto py-8">
        {messages.length === 0 ? (
          <div className="flex min-h-full flex-col justify-center">
            <div className="max-w-2xl space-y-6">
              <p className="text-sm tracking-[0.16em] text-muted-foreground uppercase">
                對話空間
              </p>
              <h1 className="font-serif text-4xl leading-tight md:text-5xl">
                你可以從任何真實的感受開始。
              </h1>
              <p className="text-lg leading-8 text-muted-foreground">
                不需要整理得很完整。Hermes 會跟著你的語氣，一步一步陪你看見正在重複出現的生命模式。
              </p>
              <div className="flex flex-wrap gap-2">
                {suggestions.map((suggestion) => (
                  <button
                    className="rounded-full border border-border bg-surface px-4 py-2 text-left text-sm text-muted-foreground transition-colors hover:border-primary hover:text-foreground"
                    key={suggestion}
                    onClick={() => setDraft(suggestion)}
                    type="button"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-5">
            {messages.map((message) => (
              <article
                className={cn(
                  "flex",
                  message.role === "user" ? "justify-end" : "justify-start",
                )}
                key={message.id}
              >
                <div
                  className={cn(
                    "max-w-[82%] rounded-2xl px-5 py-4 shadow-sm",
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-surface text-foreground",
                  )}
                >
                  {message.role === "hermes" ? (
                    <div className="prose prose-neutral max-w-none text-[1.03rem] leading-8 dark:prose-invert">
                      <ReactMarkdown>{message.text}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-wrap leading-7">{message.text}</p>
                  )}
                  <p
                    className={cn(
                      "mt-2 text-xs",
                      message.role === "user"
                        ? "text-primary-foreground/70"
                        : "text-muted-foreground",
                    )}
                  >
                    {formatTime(message.createdAt)}
                  </p>
                </div>
              </article>
            ))}
            {sending ? <TypingIndicator /> : null}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      <div className="border-t border-border bg-background py-4">
        {mapUpdated ? (
          <div className="mb-3 rounded-lg border border-primary/25 bg-primary/10 px-4 py-2 text-sm text-primary">
            ✦ 靈魂藍圖已更新
          </div>
        ) : null}
        {error ? (
          <div className="mb-3 rounded-lg border border-destructive/25 bg-destructive/10 px-4 py-2 text-sm text-destructive">
            {error}
          </div>
        ) : null}

        <div className="flex gap-3">
          <Textarea
            className="min-h-24 resize-none text-base"
            maxLength={500}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={onKeyDown}
            placeholder="慢慢說，從現在最真實的一句話開始..."
            value={draft}
          />
          <Button
            aria-label="送出訊息"
            className="h-24 w-14 bg-primary text-primary-foreground hover:bg-primary/90"
            disabled={sending || !draft.trim()}
            onClick={() => submit(draft)}
            type="button"
          >
            <Send aria-hidden="true" />
          </Button>
        </div>
        <p className="mt-2 text-right text-xs text-muted-foreground">{count}/500</p>
      </div>
    </section>
  );
}
