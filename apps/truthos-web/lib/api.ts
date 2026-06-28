export type TruthClaim = {
  axiom?: string;
  objectivity_statement?: string;
  worldly_example?: string;
  spiritual_example?: string;
};

export type ChatResponse = {
  session_id?: string;
  response?: string;
  reply?: string;
  message?: string;
  truth_layer?: {
    verified?: boolean;
    score?: number;
    properties?: string[];
    map?: {
      fact_layer?: string;
      reality_layer?: string;
      truth_claim?: TruthClaim;
      wisdom_anchor?: string;
    };
  };
  soul_map_updated?: boolean;
  guidance_overlay?: string;
  is_hard_case?: boolean;
};

export type SoulMapPattern = {
  id?: string;
  description?: string;
  dimension?: string;
  first_seen?: string;
  source_session_id?: string;
};

export type PatternWeight = {
  frequency?: number;
  weight?: number;
  last_seen?: string;
};

export type SoulMapResponse = {
  user_id: string;
  status: "active" | "not_yet_built" | string;
  message?: string;
  evolution_stage?: string;
  recurring_patterns?: SoulMapPattern[];
  recent_patterns?: string[];
  pattern_weights?: Record<string, PatternWeight>;
  active_lessons?: Array<Record<string, unknown>>;
  integrated_dimensions?: string[];
  summary?: string;
  last_truth_shift_at?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type ServiceHealth = {
  ok: boolean;
  responseTimeMs: number;
  attempts: number;
};

export type HealthStatus = "healthy" | "warming" | "partial" | "offline";

export type HealthCheckResponse = {
  truthApi: boolean;
  hermesAgent: boolean;
  status: HealthStatus;
  services: {
    truthApi: ServiceHealth;
    hermesAgent: ServiceHealth;
  };
};

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

const hermesBaseUrl =
  process.env.NEXT_PUBLIC_HERMES_AGENT_URL ||
  "https://hermes-agent-production-848a.up.railway.app";

const truthApiBaseUrl =
  process.env.NEXT_PUBLIC_TRUTH_API_URL ||
  "https://truth-api-production-0046.up.railway.app";

const sleep = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));

function isAbortError(error: unknown) {
  return error instanceof DOMException && error.name === "AbortError";
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit = {},
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    return await fetch(url, {
      ...init,
      signal: controller.signal,
    });
  } finally {
    window.clearTimeout(timer);
  }
}

async function readJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!text) {
    return {} as T;
  }

  try {
    return JSON.parse(text) as T;
  } catch {
    throw new ApiError("回應格式不是有效的 JSON", response.status, text);
  }
}

async function requestJson<T>(
  url: string,
  init?: RequestInit,
  timeoutMs = 15_000,
): Promise<T> {
  let response: Response;
  try {
    response = await fetchWithTimeout(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {}),
      },
    }, timeoutMs);
  } catch (error) {
    if (isAbortError(error)) {
      throw new ApiError("Hermes 暫時無法回應，請稍候再試", 0, error);
    }
    throw new ApiError("網路連線失敗，請稍候再試", 0, error);
  }

  const body = await readJson<T | { detail?: unknown }>(response);

  if (!response.ok) {
    const detail =
      typeof body === "object" && body && "detail" in body
        ? (body as { detail?: unknown }).detail
        : body;

    if (response.status === 422) {
      throw new ApiError("請確認訊息格式正確", 422, detail);
    }
    if (response.status === 404) {
      throw new ApiError("資料尚未建立", 404, detail);
    }
    if (response.status >= 500) {
      throw new ApiError("Hermes 暫時無法回應，請稍候再試", response.status, detail);
    }

    throw new ApiError("服務暫時無法完成請求", response.status, detail);
  }

  return body as T;
}

export async function sendChat(
  userId: string,
  message: string,
): Promise<ChatResponse> {
  return requestJson<ChatResponse>(`${hermesBaseUrl}/chat`, {
    method: "POST",
    body: JSON.stringify({
      user_id: userId,
      message,
    }),
  }, 30_000);
}

export async function getSoulMap(userId: string): Promise<SoulMapResponse> {
  return requestJson<SoulMapResponse>(
    `${truthApiBaseUrl}/api/soul-map/${encodeURIComponent(userId)}`,
    { method: "GET" },
    20_000,
  );
}

async function checkServiceHealth(url: string): Promise<ServiceHealth> {
  async function attempt(attemptNumber: number): Promise<ServiceHealth> {
    const startedAt = performance.now();
    try {
      const response = await fetchWithTimeout(
        url,
        { cache: "no-store" },
        15_000,
      );

      return {
        ok: response.ok,
        responseTimeMs: performance.now() - startedAt,
        attempts: attemptNumber,
      };
    } catch {
      return {
        ok: false,
        responseTimeMs: performance.now() - startedAt,
        attempts: attemptNumber,
      };
    }
  }

  const first = await attempt(1);
  if (first.ok) {
    return first;
  }

  await sleep(3_000);
  const second = await attempt(2);
  return second;
}

export async function checkHealth(): Promise<HealthCheckResponse> {
  const [truthApi, hermesAgent] = await Promise.all([
    checkServiceHealth(`${truthApiBaseUrl}/health`),
    checkServiceHealth(`${hermesBaseUrl}/health`),
  ]);

  const services = { truthApi, hermesAgent };
  const okCount = Number(truthApi.ok) + Number(hermesAgent.ok);
  const coldStartDetected =
    Object.values(services).some(
      (service) => service.ok && (service.responseTimeMs > 5_000 || service.attempts > 1),
    );

  let status: HealthStatus;
  if (okCount === 2) {
    status = coldStartDetected ? "warming" : "healthy";
  } else if (okCount === 1) {
    status = "partial";
  } else {
    status = "offline";
  }

  return {
    truthApi: truthApi.ok,
    hermesAgent: hermesAgent.ok,
    status,
    services,
  };
}

export function getChatText(response: ChatResponse): string {
  return response.response || response.reply || response.message || "我收到你的訊息了。";
}
