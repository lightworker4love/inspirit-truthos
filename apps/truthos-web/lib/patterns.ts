export type ParsedPattern = {
  label: string;
  description: string;
};

const knownPatterns: Record<string, ParsedPattern> = {
  "motive:MOT_001": {
    label: "核心動機",
    description: "你行動的根本驅動力，是你所有選擇的底層引擎。",
  },
  "motive:MOT_002": {
    label: "關係動機",
    description: "你在關係中尋求連結與認可的深層渴望。",
  },
  "motive:MOT_003": {
    label: "成就動機",
    description: "你對卓越與影響力的持續追求。",
  },
  "belief:BLF_001": {
    label: "核心信念",
    description: "你對自己與世界最根本的假設。",
  },
  "belief:BLF_002": {
    label: "限制性信念",
    description: "一個正在限制你行動空間的深層認知。",
  },
  "shadow:SHD_001": {
    label: "陰影面向",
    description: "一個尚未被整合的自我面向，正在從背景影響你的選擇。",
  },
  "gift:GFT_001": {
    label: "天賦特質",
    description: "你與生俱來的獨特能力，等待被更有意識地運用。",
  },
};

export function parsePattern(code: string): ParsedPattern {
  return knownPatterns[code] || {
    label: "生命模式",
    description: code,
  };
}
