from __future__ import annotations

from typing import Dict, List

# 設定別の5枚役出現確率
SETTING_PROBS: Dict[str, float] = {
    "1": 1 / 38.15,
    "2": 1 / 36.86,
    "4": 1 / 30.27,
    "5": 1 / 24.51,
    "6": 1 / 22.53,
}

# 均等事前分布（必要に応じて変更）
PRIOR_PROBS: Dict[str, float] = {k: 1.0 / len(SETTING_PROBS) for k in SETTING_PROBS}

# 456/56判定用の閾値
GOAL_THRESHOLDS = {
    "456": {
        "high_goal": 0.75,
        "high_diff": 0.15,
        "mid_goal": 0.65,
        "mid_diff": 0.07,
        "low_goal": 0.48,
        "min_sample": 120,
        "recommended_sample": 220,
    },
    "56": {
        "high_goal": 0.58,
        "high_diff": 0.08,
        "mid_goal": 0.50,
        "mid_diff": 0.04,
        "low_goal": 0.35,
        "min_sample": 160,
        "recommended_sample": 240,
    },
}

# コメント出し分け用のサンプル帯
STAGE_BOUNDS = {"early": 1000, "mid": 3000}

COMMENT_TEMPLATES: Dict[str, Dict[int, List[str]]] = {
    "early": {
        5: ["最高のロケットスタート！", "かなり強い挙動、続行推奨。"],
        4: ["序盤から高設定ムード。", "手応えあり、もう少し回して確信を。"],
        3: ["まだ判断には早いが悪くない動き。", "様子見しつつサンプル追加。"],
        2: ["ブレ幅が大きい時間帯、慎重に。", "まだ見極めは難しい状況。"],
        1: ["序盤はぶれるので深追い注意。", "無理せず撤退も選択肢。"],
    },
    "mid": {
        5: ["高設定挙動で安定中。", "攻め継続でOK。"],
        4: ["強めの気配、かなり前向き。", "追加サンプルで確度を上げよう。"],
        3: ["どっちつかず、あと少しで見える。", "継続か撤退か、もう一押しで判断。"],
        2: ["期待値は低め、慎重に。", "引き際を意識しながら回そう。"],
        1: ["分が悪い展開。", "他台検討もアリ。"],
    },
    "late": {
        5: ["閉店までブン回しレベル。", "勝負あり、走り切ろう。"],
        4: ["かなり強い、押し通して良さそう。", "残り時間と相談しつつ続行。"],
        3: ["やや優勢だが決め手に欠ける。", "深追いは計画的に。"],
        2: ["リスク寄り、追うなら根拠を。", "無理は禁物。"],
        1: ["撤退推奨。", "傷が浅いうちに切り替え。"],
    },
}

# プログレスバーなどの色
SETTING_COLORS = {
    "1": "#7a7a7a",
    "2": "#4a4a4a",
    "4": "#f0c419",
    "5": "#ff9f43",
    "6": "#ff6b6b",
}

ACCENT_BLUE = "#3a9bdc"
STAR_GOLD = "#ffd700"
BG_DARK = "#0f0f0f"
CARD_DARK = "#1a1a1a"
