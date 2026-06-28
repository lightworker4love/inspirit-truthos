# ISP-TRUTH-ARCH-002

# 《Platform Module Mapping：從 Connectome 到 Truth Graph》
**in spirit AI 智慧平台 | 技術對齊文件 v1.0**

***

## 一、映射框架總覽

| 果蠅實驗組件 | 生物功能 | truthOS 對應模組 | 平台功能 |
|---|---|---|---|
| FlyWire Connectome（14萬神經元圖譜）| 完整神經接線圖，是行為的先天藍圖 | **Truth Graph**（12維 × 100心法 × 10,000拼圖）| 真理的先天藍圖，是智慧推理的基礎骨架 |
| Leaky Integrate-and-Fire 模型 | 神經元間電化學激活規則 | **Truth Inference Engine**（Truth Classifier + Reasoning Engine）| 問題輸入如何激活對應的真理拼圖與推理路徑 |
| 傳入神經元（Afferent Neurons） | 接收外部感知信號輸入 | **Query Router + Session Manager** | 接收使用者問題，判斷深度、面向、風險等級 |
| 中樞神經元（Interneurons） | 複雜信號處理與整合 | **Truth Classifier + Dimension Selector + Context Fusion** | 讀取 Soul Map，融合當前情境，選取對應面向與心法 |
| 傳出神經元（Efferent Neurons）| 發送運動指令，驅動行為 | **Guided Synthesis Layer** | 結構化輸出：看見處境 → 真理視角 → 提問 → 行動 |
| 虛擬軀體（87關節 MuJoCo）| 讓大腦有具身化載體，完成感知-行動閉環 | **Soul Map Engine + Blind Spot Archive + Belief Log** | 讓真理有個人化記憶載體，完成感知-引導-成長閉環 |
| 物理模擬引擎（MuJoCo）| 物理環境，提供真實感知與反作用力 | **Local Infra（FastAPI + LanceDB + Qdrant + Mem0）** | 數位環境，提供真實個案脈絡與長期記憶反作用力 |
| 環境回授（Environment Feedback）| 外部世界信號回流大腦，持續調整行為 | **Evolution Writeback（blind_spot / belief_log / soul_map 回寫）**| 每次對話結果回寫至長期記憶，讓系統持續演化 |
| 果蠅行為（覓食、清潔、爬行）| 行為湧現，可被觀察與驗證 | **TruthOS 回應輸出** | 引導湧現，可被 Coach Review Layer 審核與校準 |

***

## 二、閉環對比圖

**果蠅具身化閉環：**
```
[虛擬環境刺激]
      ↓
[傳入神經元：感知信號輸入]
      ↓
[14萬中樞神經元：生物物理計算]
      ↓
[傳出神經元：動作指令輸出]
      ↓
[87關節虛擬身體：執行動作]
      ↓
[環境物理回授：新刺激產生]
      ↓（循環）
```

**truthOS 智慧閉環：**
```
[使用者提問/生命事件]
      ↓
[Query Router：問題分型（問題型/面向型/深度型/風險型）]
      ↓
[Context Fusion：讀取 Soul Map + Session 記憶 + Agent persona]
      ↓
[Hybrid Retrieval：Qdrant 語意 + LanceDB 高精度方法論]
      ↓
[Truth Discernment：覺幻機制（事實/解讀/推論/建議 分層）]
      ↓
[Guided Synthesis：結構化輸出（看見/真理視角/提問/行動）]
      ↓
[Evolution Writeback：blind_spot + belief_log + soul_map 回寫]
      ↓（循環，個案繼續成長）
```

***

## 三、關鍵升維模組：果蠅沒有，truthOS 必須有

果蠅實驗目前缺乏記憶演化與治理機制，這也是它的研究局限。 truthOS 在此處超越：

**A. Truth Discernment Layer（覺幻機制）**
果蠅的神經元不需要區分「這是真實的香蕉還是假的香蕉」，它只有物理感知。但 AI 的最大危機是：**模型會講得很像真理，但不一定是真理**。
所以 truthOS 必須在輸出前強制執行：
- 這是 fact？還是個人 reality？還是 truth？
- 這是推論？猜測？還是暫時詮釋？
- 達到「有道理未必是真理」的系統性防呆

**B. Coach Review Layer（人類校準層）**
果蠅沒有教練可以從外部批注。 但 truthOS 設計了人類教練審閱機制，讓 truth_evals（grounded_score / discernment_score / warmth_score / hallucination_risk_score）能被批注並回寫至 prompt，這是系統真正長出智慧的校準路徑。

**C. Three-Heart Architecture（三顆心臟）**
```
OpenClaw（做事心臟）
Second Me（說話心臟）
TruthOS（辨理心臟）  ← 果蠅沒有這一層
```
這是 in spirit AI 與所有「具身智能」最本質的差距：不只能動，還能辨理。

***

## 四、Schema 直接對齊

| 果蠅數據結構 | truthOS 對應資料表 |
|---|---|
| Connectome Graph（神經元節點 + 突觸邊）| `truth_dimensions` + `core_principles` + `puzzle_relations` |
| Synapse firing rules（突觸激活規則）| `truth_puzzles`（statement + trigger_signals + truth_reframe）|
| Behavior trajectory（行為軌跡 95% 比對）| `truth_evals`（grounded_score + discernment_score 評測）|
| No memory / no learning（當前版本）| `soul_maps` + `blind_spot_archives` + `belief_logs`（truthOS 的學習記憶層）|
