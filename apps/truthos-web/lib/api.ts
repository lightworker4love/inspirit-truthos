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

async function requestJson<T>(url: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {}),
      },
    });
  } catch (error) {
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
  });
}

export async function getSoulMap(userId: string): Promise<SoulMapResponse> {
  return requestJson<SoulMapResponse>(
    `${truthApiBaseUrl}/api/soul-map/${encodeURIComponent(userId)}`,
    { method: "GET" },
  );
}

export async function checkHealth(): Promise<{
  truthApi: boolean;
  hermesAgent: boolean;
}> {
  const [truthApi, hermesAgent] = await Promise.allSettled([
    fetch(`${truthApiBaseUrl}/health`, { cache: "no-store" }),
    fetch(`${hermesBaseUrl}/health`, { cache: "no-store" }),
  ]);

  return {
    truthApi: truthApi.status === "fulfilled" && truthApi.value.ok,
    hermesAgent: hermesAgent.status === "fulfilled" && hermesAgent.value.ok,
  };
}

export function getChatText(response: ChatResponse): string {
  return response.response || response.reply || response.message || "我收到你的訊息了。";
}
