export function TypingIndicator() {
  return (
    <div className="flex w-fit items-center gap-1 rounded-2xl bg-surface px-4 py-3">
      <span className="size-2 rounded-full bg-muted-foreground" />
      <span className="size-2 rounded-full bg-muted-foreground" />
      <span className="size-2 rounded-full bg-muted-foreground" />
      <span className="sr-only">Hermes 正在回應</span>
    </div>
  );
}
