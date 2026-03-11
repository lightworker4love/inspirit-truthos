from __future__ import annotations

from collections import Counter
from collections.abc import Sequence


def compose_response(question: str, puzzles: Sequence[dict]) -> dict[str, str]:
    if not puzzles:
        return {
            "mirror": f"你提到的是：{question.strip()}",
            "truth_view": "目前沒有足夠的 Truth Puzzle 可供推理，先聚焦在你最在意的互動與感受。",
            "coach_question": "這件事裡，你最想被理解的是哪個部分？",
            "action": "先補建向量索引，或重新描述情境中的人、情緒與衝突。",
        }

    lead = puzzles[0]
    dimension_counts = Counter(puzzle["dimension_code"] for puzzle in puzzles)
    leading_dimension = dimension_counts.most_common(1)[0][0]
    principles = list(dict.fromkeys(puzzle["principle_code"] for puzzle in puzzles[:3]))

    return {
        "mirror": f"你描述的情境接近「{lead['title']}」這類模式，核心張力是 {lead['statement']}",
        "truth_view": (
            f"目前檢索結果顯示，議題主要落在 {leading_dimension} 維度，"
            f"並與 {', '.join(principles)} 這些 principle 有關。"
            f"常見誤區是「{lead['misbelief']}」，較完整的真相重構是「{lead['truth_reframe']}」。"
        ),
        "coach_question": lead["coach_prompt"],
        "action": f"先用「{lead['truth_reframe']}」校正觀點，然後在下一次互動前刻意練習一個更清楚的界線或選擇。",
    }
