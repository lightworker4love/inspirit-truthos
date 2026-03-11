from __future__ import annotations

from collections import defaultdict

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


def classify_dimensions(message: str, top_k: int = 3) -> list[str]:
    text = message.strip().lower()
    if not text:
        return DIMENSIONS[:top_k]

    scores: dict[str, float] = defaultdict(float)
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
        for dimension in DIMENSIONS:
            scores[dimension] = 0.0

    ranked = sorted(
        DIMENSIONS,
        key=lambda dimension: (-scores[dimension], DIMENSIONS.index(dimension)),
    )
    return ranked[:top_k]
