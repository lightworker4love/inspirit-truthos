from __future__ import annotations

import os
import re
from collections import defaultdict

from openai import OpenAI

from app.config import get_chat_model, get_dimension_classifier_llm_fallback

DIMENSIONS = [
    "motive",
    "cognition",
    "emotion",
    "relationship",
    "belief",
    "evolution",
    "causality",
    "manifestation",
    "suffering",
    "freedom",
    "compassion",
    "discernment",
]

DIMENSION_KEYWORDS = {
    "motive": ["動機", "motive", "討好", "控制", "認可", "證明", "想被看見", "交換", "付出"],
    "cognition": ["認知", "cognition", "想法", "解讀", "誤會", "腦補", "推論", "標籤", "以為"],
    "emotion": ["情緒", "emotion", "生氣", "焦慮", "難過", "委屈", "羞愧", "恐慌", "嫉妒"],
    "relationship": ["關係", "relationship", "伴侶", "家人", "家庭", "朋友", "界線", "互動", "衝突"],
    "belief": ["信念", "belief", "價值感", "不配得", "一定要", "必須", "應該", "證明自己"],
    "evolution": ["進化", "evolution", "成長", "重複", "課題", "卡住", "學習", "模式", "循環"],
    "causality": ["因果", "causality", "後果", "結果", "責任", "選擇", "代價", "拖延", "回饋"],
    "manifestation": ["顯化", "manifestation", "金錢", "收入", "資源", "價值交換", "匱乏", "市場"],
    "suffering": ["痛苦", "suffering", "受傷", "失落", "崩潰", "創傷", "受害", "折磨", "痛"],
    "freedom": ["自由", "freedom", "束縛", "選擇", "逃開", "承諾", "角色", "獨立", "反抗"],
    "compassion": ["慈悲", "compassion", "照顧", "幫助", "同理", "溫柔", "善良", "耗盡", "承擔"],
    "discernment": ["辨識", "discernment", "真相", "判斷", "直覺", "分辨", "混亂", "看清", "事實"],
}

RELATIONAL_CONTEXT = ["伴侶", "家人", "家庭", "朋友", "同事", "關係", "婚姻", "親子"]
CARE_CONTEXT = ["幫", "幫助", "照顧", "救", "支持", "接住"]
CLASSIFIER_SYSTEM_PROMPT = (
    "你是 in spirit 意識分析引擎。\n"
    "從以下 12 個維度中，選出最符合用戶描述的前 3 個，只回傳逗號分隔的代碼：\n"
    "motive, cognition, emotion, relationship, belief, evolution,\n"
    "causality, manifestation, suffering, freedom, compassion, discernment"
)


def _keyword_scores(message: str) -> dict[str, float]:
    text = message.strip().lower()
    scores: dict[str, float] = defaultdict(float)
    if not text:
        return {dimension: 0.0 for dimension in DIMENSIONS}

    for dimension in DIMENSIONS:
        for keyword in DIMENSION_KEYWORDS[dimension]:
            token = keyword.lower()
            if token in text:
                scores[dimension] += max(len(token) / 4, 1.0)

    if any(token.lower() in text for token in RELATIONAL_CONTEXT):
        scores["relationship"] += 2.5
    if any(token.lower() in text for token in CARE_CONTEXT):
        scores["compassion"] += 1.5
    if "控制" in text and any(token.lower() in text for token in RELATIONAL_CONTEXT):
        scores["relationship"] += 1.5

    if not scores:
        return {dimension: 0.0 for dimension in DIMENSIONS}
    return {dimension: float(scores.get(dimension, 0.0)) for dimension in DIMENSIONS}


def _rank_dimensions(scores: dict[str, float], top_k: int) -> list[str]:
    ranked = sorted(
        DIMENSIONS,
        key=lambda dimension: (-scores[dimension], DIMENSIONS.index(dimension)),
    )
    return ranked[:top_k]


def _llm_fallback_needed(scores: dict[str, float]) -> bool:
    top_score = max(scores.values(), default=0.0)
    return top_score < 1.0


def _parse_dimension_codes(raw: str, top_k: int) -> list[str]:
    tokens = [token.strip().lower() for token in re.split(r"[,，\n]+", raw) if token.strip()]
    picked: list[str] = []
    for token in tokens:
        if token in DIMENSIONS and token not in picked:
            picked.append(token)
        if len(picked) >= top_k:
            break
    return picked


def _llm_dimension_fallback(message: str, top_k: int) -> list[str]:
    client = OpenAI(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    response = client.chat.completions.create(
        model=get_chat_model(),
        temperature=0,
        messages=[
            {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
            {"role": "user", "content": f"用戶描述：{message.strip()}"},
        ],
    )
    content = response.choices[0].message.content or ""
    return _parse_dimension_codes(content, top_k)


def classify_dimensions(message: str, top_k: int = 3) -> list[str]:
    text = message.strip()
    if not text:
        return DIMENSIONS[:top_k]

    scores = _keyword_scores(text)
    ranked = _rank_dimensions(scores, top_k)

    if get_dimension_classifier_llm_fallback() and _llm_fallback_needed(scores):
        try:
            llm_ranked = _llm_dimension_fallback(text, top_k)
            if llm_ranked:
                return llm_ranked
        except Exception:
            pass

    return ranked
