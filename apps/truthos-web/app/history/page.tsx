import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

export default function HistoryPage() {
  return (
    <section className="mx-auto flex min-h-[calc(100vh-8rem)] max-w-2xl flex-col justify-center px-6 py-12">
      <Card className="border-border bg-surface">
        <CardContent className="space-y-5 p-8">
          <p className="text-sm tracking-[0.16em] text-muted-foreground uppercase">
            History
          </p>
          <h1 className="font-serif text-5xl leading-tight">對話記錄</h1>
          <p className="text-lg leading-8 text-muted-foreground">
            這個功能即將開放，你過去的每一次對話都將被完整保留。
          </p>
          <Link
            className="inline-flex h-11 w-fit items-center gap-2 rounded-lg bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            href="/chat"
          >
            回到對話 <ArrowRight aria-hidden="true" className="size-4" />
          </Link>
        </CardContent>
      </Card>
    </section>
  );
}
