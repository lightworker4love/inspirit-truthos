from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEEDS_DIR = ROOT / "data/seeds"
SOURCE_DOC = "TruthOS seed dataset"

CONTEXTS = [
    {"scene": "家庭對話", "tag": "家庭", "use_cases": ["家庭", "親子"]},
    {"scene": "伴侶衝突", "tag": "伴侶", "use_cases": ["伴侶", "界線"]},
    {"scene": "職場協作", "tag": "職場", "use_cases": ["工作", "團隊"]},
    {"scene": "領導決策", "tag": "領導", "use_cases": ["領導", "決策"]},
    {"scene": "朋友互動", "tag": "友誼", "use_cases": ["友誼", "界線"]},
    {"scene": "金錢選擇", "tag": "金錢", "use_cases": ["金錢", "價值"]},
    {"scene": "健康壓力", "tag": "健康", "use_cases": ["健康", "壓力"]},
    {"scene": "創作卡關", "tag": "創作", "use_cases": ["創作", "表達"]},
    {"scene": "靈性實踐", "tag": "靈性", "use_cases": ["靈性", "自我觀察"]},
    {"scene": "重大失落", "tag": "失落", "use_cases": ["失落", "轉化"]},
    {"scene": "教養現場", "tag": "教養", "use_cases": ["親子", "教養"]},
    {"scene": "團隊回饋", "tag": "回饋", "use_cases": ["團隊", "回饋"]},
    {"scene": "社群曝光", "tag": "社群", "use_cases": ["社群", "自我價值"]},
]

STATEMENT_SUFFIXES = [
    "，讓對話逐漸失衡。",
    "，讓界線變得模糊。",
    "，讓責任位置變得混亂。",
    "，使真正的需求被遮住。",
    "，讓反饋失去作用。",
    "，讓信任開始鬆動。",
    "，讓決定越來越僵硬。",
    "，讓內在更難安定。",
    "，使互動落入重複循環。",
    "，讓看見真相的空間縮小。",
    "，讓支持變成壓力。",
    "，讓改變停在表面。",
    "，讓資源交換變得扭曲。",
]

DIMENSIONS = [
    {
        "code": "motive",
        "name_zh": "動機",
        "prefix": "MOT",
        "themes": ["討好", "交易", "補償", "炫耀", "恐懼", "控制", "匱乏", "罪惡感", "認可"],
        "title_pattern": "{theme}驅動的付出",
        "axiom": "當{theme}主導動機時，行動容易脫離真心。",
        "misbelief": "只要沒有{theme}，我就不會被需要。",
        "reframe": "真實動機不必用{theme}換取位置。",
        "prompt": "如果不靠{theme}，你還想守護什麼？",
        "statement": "在{scene}中，表面上是在付出，實際上卻被{theme}推著走",
    },
    {
        "code": "cognition",
        "name_zh": "認知",
        "prefix": "COG",
        "themes": ["投射", "過度推論", "二分法", "腦補", "先入為主", "標籤化", "自我否定", "災難化", "選擇性失明"],
        "title_pattern": "{theme}式解讀",
        "axiom": "認知一旦被{theme}綁架，事實就會被解釋成威脅。",
        "misbelief": "我的第一個解讀若帶著{theme}，那就一定是真相。",
        "reframe": "{theme}只是其中一種解讀，不是全部事實。",
        "prompt": "拿掉{theme}後，還有哪些事實仍然成立？",
        "statement": "在{scene}中，先用{theme}解讀局面，忽略了可被驗證的事實",
    },
    {
        "code": "emotion",
        "name_zh": "情緒",
        "prefix": "EMO",
        "themes": ["壓抑", "爆發", "麻木", "羞恥", "焦慮", "怨恨", "恐慌", "嫉妒", "委屈"],
        "title_pattern": "{theme}情緒回路",
        "axiom": "當情緒停在{theme}，感受就難以指向真正需要。",
        "misbelief": "只要我感到{theme}，外界就一定應該改變。",
        "reframe": "{theme}是訊號，不是完整結論。",
        "prompt": "{theme}底下那個還沒被承認的需要是什麼？",
        "statement": "在{scene}中，情緒停在{theme}，於是聽不見更深層的需要",
    },
    {
        "code": "relationship",
        "name_zh": "關係",
        "prefix": "REL",
        "themes": ["拯救", "依附", "討好", "防衛", "測試", "佔有", "退縮", "角色錯位", "界線模糊"],
        "title_pattern": "{theme}型關係模式",
        "axiom": "關係若被{theme}主導，連結會慢慢變成束縛。",
        "misbelief": "沒有{theme}，這段關係就撐不住。",
        "reframe": "關係需要真實與界線，不需要用{theme}維持。",
        "prompt": "你現在是在連結，還是在用{theme}保住位置？",
        "statement": "在{scene}中，用{theme}維持靠近，反而讓彼此更難真實相遇",
    },
    {
        "code": "belief",
        "name_zh": "信念",
        "prefix": "BEL",
        "themes": ["不配得", "必須完美", "先苦後值", "被看見才算存在", "服從才安全", "失敗等於否定", "需要證明", "改變很危險"],
        "title_pattern": "{theme}信念",
        "axiom": "信念若被{theme}固定，選擇就會被舊故事限制。",
        "misbelief": "如果不按照{theme}活，我就沒有價值。",
        "reframe": "{theme}只是舊信念的語氣，不是你的本質。",
        "prompt": "哪個舊故事讓你把{theme}當成唯一答案？",
        "statement": "在{scene}中，被{theme}的內在敘事綁住，因此不敢做新的選擇",
    },
    {
        "code": "evolution",
        "name_zh": "進化",
        "prefix": "EVO",
        "themes": ["重複課題", "抗拒改變", "停留舒適圈", "把挫折當倒退", "急著畢業", "模仿成長", "只收結果", "逃避整合"],
        "title_pattern": "{theme}成長課題",
        "axiom": "成長若卡在{theme}，重複就會偽裝成命運。",
        "misbelief": "我必須透過{theme}，才算真的在成長。",
        "reframe": "成長來自整合，不來自反覆抓住{theme}。",
        "prompt": "如果不再重演{theme}，下一步成熟會是什麼？",
        "statement": "在{scene}中，持續用{theme}看待成長，於是重複同一個課題",
    },
    {
        "code": "causality",
        "name_zh": "因果",
        "prefix": "CAU",
        "themes": ["推責", "短視近利", "重複相同選擇", "忽視代價", "只看結果", "情緒下決定", "拖延", "切斷反饋"],
        "title_pattern": "{theme}因果盲點",
        "axiom": "忽略{theme}時，因與果之間的責任會被切斷。",
        "misbelief": "只要結果過得去，{theme}就不重要。",
        "reframe": "看見{theme}背後的選擇，才能真正改變結果。",
        "prompt": "這個結果之前，你在哪個選擇點忽略了{theme}？",
        "statement": "在{scene}中，因為忽略{theme}，看不見結果其實來自一連串選擇",
    },
    {
        "code": "manifestation",
        "name_zh": "顯化",
        "prefix": "MAN",
        "themes": ["匱乏感", "價格焦慮", "拿價值換認同", "急著顯化", "討好市場", "不敢接收", "過度控制結果", "把金錢神化"],
        "title_pattern": "{theme}式顯化",
        "axiom": "顯化若被{theme}牽動，追求就會偏離價值交換。",
        "misbelief": "只有靠{theme}，我才能得到想要的資源。",
        "reframe": "價值交換比{theme}更能穩定地帶來資源。",
        "prompt": "若不再用{theme}追資源，你真正要交換的是什麼價值？",
        "statement": "在{scene}中，想要創造結果，卻被{theme}拉回匱乏與緊抓",
    },
    {
        "code": "suffering",
        "name_zh": "痛苦",
        "prefix": "SUF",
        "themes": ["受害者認同", "抗拒疼痛", "麻醉自己", "比較傷口", "放大失落", "反覆咀嚼", "用痛換關注", "拒絕求助"],
        "title_pattern": "{theme}型痛苦循環",
        "axiom": "痛苦一旦與{theme}結盟，傷口就會變成身份。",
        "misbelief": "若失去{theme}，別人就不會理解我的痛。",
        "reframe": "承認痛苦不等於繼續住在{theme}裡。",
        "prompt": "當你放下{theme}時，痛苦想教你的會是什麼？",
        "statement": "在{scene}中，把{theme}黏在痛苦上，讓傷口變得更難流動",
    },
    {
        "code": "freedom",
        "name_zh": "自由",
        "prefix": "FRE",
        "themes": ["害怕承諾", "假性自由", "依賴外部許可", "逃避責任", "害怕失去選項", "把反抗當自由", "過度獨立", "被角色綁住"],
        "title_pattern": "{theme}型自由假象",
        "axiom": "自由若建立在{theme}上，選擇看似開闊卻仍被束縛。",
        "misbelief": "只有維持{theme}，我才算自由。",
        "reframe": "自由不是維持{theme}，而是能承擔選擇。",
        "prompt": "若不把{theme}叫做自由，你真正想鬆開的是什麼？",
        "statement": "在{scene}中，把{theme}誤認成自由，因此逃開了真正的承擔",
    },
    {
        "code": "compassion",
        "name_zh": "慈悲",
        "prefix": "COM",
        "themes": ["過度承擔", "慈悲疲勞", "同情替代理解", "把付出當價值", "不會接住自己", "溫柔失去界線", "用善良避衝突", "忽略自身需要"],
        "title_pattern": "{theme}式慈悲失衡",
        "axiom": "慈悲若失去中心而落入{theme}，付出就會耗損生命力。",
        "misbelief": "如果不靠{theme}回應他人，我就是自私。",
        "reframe": "真正的慈悲能照顧他人，也能鬆開{theme}。",
        "prompt": "少一點{theme}之後，你還能怎麼溫柔而清楚地回應？",
        "statement": "在{scene}中，出於{theme}去照顧別人，最後連自己也被耗盡",
    },
    {
        "code": "discernment",
        "name_zh": "辨識",
        "prefix": "DIS",
        "themes": ["把直覺當結論", "只挑想聽的", "權威依賴", "道德優越", "真假混用", "語氣取代內容", "急著定義", "害怕看見複雜"],
        "title_pattern": "{theme}辨識偏差",
        "axiom": "辨識若被{theme}遮住，真相就會被立場取代。",
        "misbelief": "只要我避開{theme}的不舒服，就能更快看見真相。",
        "reframe": "真相不怕複雜，先放下{theme}才看得更清楚。",
        "prompt": "若先暫停{theme}，你會重新檢查哪個訊號？",
        "statement": "在{scene}中，讓{theme}主導判斷，於是真相被偏好的說法覆蓋",
    },
]


def render_jsonl(path: Path, rows: list[dict]) -> None:
    lines = [json.dumps(row, ensure_ascii=False) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_core_principles() -> tuple[list[dict], dict[str, list[dict]]]:
    rows: list[dict] = []
    principles_by_dimension: dict[str, list[dict]] = {}

    for dimension in DIMENSIONS:
        principles: list[dict] = []
        for index, theme in enumerate(dimension["themes"], start=1):
            row = {
                "id": f"cp_{dimension['prefix'].lower()}_{index:03d}",
                "dimension_code": dimension["code"],
                "code": f"{dimension['prefix']}_{index:03d}",
                "title": dimension["title_pattern"].format(theme=theme),
                "axiom": dimension["axiom"].format(theme=theme),
            }
            rows.append(row)
            principles.append(
                {
                    "code": row["code"],
                    "theme": theme,
                    "title": row["title"],
                    "misbelief": dimension["misbelief"].format(theme=theme),
                    "truth_reframe": dimension["reframe"].format(theme=theme),
                    "coach_prompt": dimension["prompt"].format(theme=theme),
                    "statement_template": dimension["statement"],
                    "dimension_code": dimension["code"],
                    "dimension_name_zh": dimension["name_zh"],
                }
            )
        principles_by_dimension[dimension["code"]] = principles

    return rows, principles_by_dimension


def build_truth_puzzles(principles_by_dimension: dict[str, list[dict]]) -> list[dict]:
    rows: list[dict] = []

    for dimension in DIMENSIONS:
        principles = principles_by_dimension[dimension["code"]]
        base_count, remainder = divmod(100, len(principles))
        dimension_sequence = 1

        for principle_index, principle in enumerate(principles):
            puzzle_count = base_count + (1 if principle_index < remainder else 0)

            for variant_index in range(puzzle_count):
                context = CONTEXTS[(principle_index + variant_index) % len(CONTEXTS)]
                suffix = STATEMENT_SUFFIXES[(dimension_sequence - 1) % len(STATEMENT_SUFFIXES)]
                title = f"{context['scene']}中的{principle['theme']}盲點"
                statement = principle["statement_template"].format(scene=context["scene"], theme=principle["theme"]) + suffix
                tags = [dimension["name_zh"], principle["theme"], context["tag"]]
                embedding_text = " ".join(
                    [
                        dimension["code"],
                        dimension["name_zh"],
                        principle["code"],
                        principle["theme"],
                        title,
                        statement,
                        principle["misbelief"],
                        principle["truth_reframe"],
                        *tags,
                        *context["use_cases"],
                    ]
                )

                rows.append(
                    {
                        "id": f"tp_{dimension['prefix'].lower()}_{dimension_sequence:03d}",
                        "dimension_code": dimension["code"],
                        "principle_code": principle["code"],
                        "title": title,
                        "statement": statement,
                        "misbelief": principle["misbelief"],
                        "truth_reframe": principle["truth_reframe"],
                        "coach_prompt": principle["coach_prompt"],
                        "tags": tags,
                        "use_cases": context["use_cases"],
                        "source_doc": SOURCE_DOC,
                        "embedding_text": embedding_text,
                    }
                )
                dimension_sequence += 1

    return rows


def main() -> int:
    SEEDS_DIR.mkdir(parents=True, exist_ok=True)
    principles, principles_by_dimension = build_core_principles()
    puzzles = build_truth_puzzles(principles_by_dimension)

    render_jsonl(SEEDS_DIR / "core_principles.seed.jsonl", principles)
    render_jsonl(SEEDS_DIR / "truth_puzzles.seed.jsonl", puzzles)

    print(f"Wrote {len(principles)} principles to {SEEDS_DIR / 'core_principles.seed.jsonl'}")
    print(f"Wrote {len(puzzles)} puzzles to {SEEDS_DIR / 'truth_puzzles.seed.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
