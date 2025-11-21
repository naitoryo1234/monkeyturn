from __future__ import annotations

import math
from typing import Dict, Tuple, Optional

from .constants import GOAL_THRESHOLDS, PRIOR_PROBS, SETTING_COLORS, SETTING_PROBS, STAGE_BOUNDS

BASE_COMMENTS = {
    "early": {
        5: "[序盤/優勢] 強いサンプル。続行で精度を上げよう。",
        4: "[序盤/良好] 手応えあり。もう少し回して確信を。",
        3: "[序盤/拮抗] まだ揺れる帯域。追加サンプル推奨。",
        2: "[序盤/弱め] ブレが大きい時間帯。慎重に。",
        1: "[序盤/劣勢] 早期撤退も選択肢。深追い注意。",
    },
    "mid": {
        5: "[中盤/優勢] 高設定寄りで安定。続行推奨。",
        4: "[中盤/良好] 強めの気配。もう少しで決め手。",
        3: "[中盤/拮抗] 決め手不足。追加サンプルを。",
        2: "[中盤/劣勢] 期待値低め。引き際を意識。",
        1: "[中盤/悪化] 分が悪い。撤退検討を。",
    },
    "late": {
        5: "[終盤/確信] ブン回しレベル。決断済みでOK。",
        4: "[終盤/優勢] 強いが時間と相談。",
        3: "[終盤/拮抗] 微差。深追いは計画的に。",
        2: "[終盤/劣勢] リスク寄り。無理は禁物。",
        1: "[終盤/撤退] 切り上げ推奨。",
    },
}


def calculate_likelihood(num_spins: int, num_hits: int, p: float) -> float:
    if num_spins < 0 or num_hits < 0 or num_hits > num_spins:
        return 0.0
    if p <= 0.0 or p >= 1.0:
        return 0.0
    log_nCk = (
        math.lgamma(num_spins + 1)
        - math.lgamma(num_hits + 1)
        - math.lgamma(num_spins - num_hits + 1)
    )
    log_likelihood = log_nCk + num_hits * math.log(p) + (num_spins - num_hits) * math.log(1.0 - p)
    return math.exp(log_likelihood)


def compute_posteriors(num_spins: int, num_hits: int) -> Dict[str, float]:
    if num_spins <= 0:
        return PRIOR_PROBS.copy()

    weighted: Dict[str, float] = {}
    for setting, p in SETTING_PROBS.items():
        likelihood = calculate_likelihood(num_spins, num_hits, p)
        weighted[setting] = PRIOR_PROBS.get(setting, 0.0) * likelihood

    total = sum(weighted.values())
    if total <= 0.0:
        return PRIOR_PROBS.copy()

    return {k: v / total for k, v in weighted.items()}


def summarize(num_spins: int, num_hits: int) -> Dict[str, float]:
    posteriors = compute_posteriors(num_spins, num_hits)
    prob_456 = sum(posteriors.get(s, 0.0) for s in ("4", "5", "6"))
    prob_56 = sum(posteriors.get(s, 0.0) for s in ("5", "6"))
    observed_rate = (num_spins / num_hits) if num_hits > 0 and num_spins > 0 else None
    return {
        "posteriors": posteriors,
        "prob_456": prob_456,
        "prob_56": prob_56,
        "observed_rate": observed_rate,
    }


def evaluate_goal(goal_code: str, goal_prob: float, alt_prob: float, sample_n: int) -> Tuple[int, str]:
    th = GOAL_THRESHOLDS[goal_code]
    diff = goal_prob - alt_prob
    recommended = th.get("recommended_sample", th["min_sample"])
    sample_ratio = sample_n / recommended if recommended > 0 else 1.0

    if sample_n < th["min_sample"]:
        if goal_prob >= th["mid_goal"] or diff >= th["mid_diff"]:
            return 3, "sample_strong"
        return 1, "sample_low"

    rating = 2
    tag = "ok"
    if goal_prob >= th["high_goal"] or diff >= th["high_diff"]:
        rating = 4
        if goal_prob >= th["high_goal"] + 0.08 or diff >= th["high_diff"] * 1.3:
            rating = 5
    elif goal_prob >= th["mid_goal"] or diff >= th["mid_diff"]:
        rating = 3
    elif goal_prob < th["low_goal"]:
        rating = 1 if diff < 0 else 2

    if sample_ratio < 0.7 and rating > 1:
        rating -= 1
        tag = "sample_caution"

    return rating, tag


def stage_from_sample(sample_n: int) -> str:
    if sample_n < STAGE_BOUNDS["early"]:
        return "early"
    if sample_n < STAGE_BOUNDS["mid"]:
        return "mid"
    return "late"


def prob_strength(goal_code: str, goal_prob: float, alt_prob: float) -> str:
    th = GOAL_THRESHOLDS[goal_code]
    diff = goal_prob - alt_prob
    if goal_prob >= th["high_goal"] or diff >= th["high_diff"]:
        return "strong"
    if goal_prob >= th["mid_goal"] or diff >= th["mid_diff"]:
        return "good"
    if goal_prob < th["low_goal"]:
        return "weak"
    return "even"


def sample_status(goal_code: str, sample_n: int) -> Tuple[str, int]:
    th = GOAL_THRESHOLDS[goal_code]
    recommended = th.get("recommended_sample", th["min_sample"])
    remain = max(recommended - sample_n, 0)
    ratio = sample_n / recommended if recommended > 0 else 1.0
    if ratio >= 1.0:
        return "enough", remain
    if ratio >= 0.7:
        return "almost", remain
    return "thin", remain


def build_comment(
    goal_code: str,
    goal_prob: float,
    alt_prob: float,
    sample_n: int,
    rating: int,
    tag: str,
) -> str:
    stage = stage_from_sample(sample_n)
    base = BASE_COMMENTS.get(stage, {}).get(rating) or BASE_COMMENTS.get(stage, {}).get(3) or ""

    strength = prob_strength(goal_code, goal_prob, alt_prob)
    status, remain = sample_status(goal_code, sample_n)
    strength_text = {
        "strong": "優勢",
        "good": "良好",
        "even": "拮抗",
        "weak": "劣勢",
    }.get(strength, "拮抗")

    sample_note = ""
    if status == "thin":
        sample_note = f"データ薄め。あと{remain}Gで精度アップ。"
        if strength in ("strong", "good"):
            sample_note = f"手応えは{strength_text}だが、{sample_note}"
    elif status == "almost":
        sample_note = f"推奨まで残り{remain}G。"
    elif status == "enough" and strength == "weak":
        sample_note = "データは十分。挽回は薄い可能性。"

    if tag == "sample_low":
        sample_note = "サンプル不足。まずは回転数を稼いで再評価。"
    elif tag == "sample_strong":
        sample_note = f"手応えは強いがサンプル不足。あと{remain}Gで確度を上げよう。"
    elif tag == "sample_caution" and strength in ("strong", "good"):
        sample_note = sample_note or "手応えはあるがデータは少なめ。"

    if sample_note:
        return f"{base} {sample_note}".strip()
    return base


def build_alignment_comment(prob_456: float, prob_56: float) -> str:
    gap = prob_456 - prob_56
    if prob_456 < 0.25:
        return "全体的に弱め。"
    if prob_456 >= 0.5 and prob_56 < 0.25:
        return "設定4は見えるが56は薄め。中間寄りを警戒。"
    if gap >= 0.15 and prob_456 >= 0.35:
        return "456寄りだが56は厳しい。中間を疑う。"
    if prob_56 >= 0.5:
        return "56がかなり強い。高設定に期待。"
    if prob_56 >= 0.35 and prob_456 >= 0.5:
        return "56にも十分期待できるレンジ。"
    return ""


def format_observed_rate(num_spins: int, num_hits: int) -> str:
    # 常に計算する（ヒット0や回転0を特例表示）
    if num_hits <= 0:
        return "ヒットなし"
    if num_spins <= 0:
        return "回転不足"
    return f"1/{(num_spins/num_hits):.1f}"


def build_share_text(
    num_spins: int,
    num_hits: int,
    prob_456: float,
    prob_56: float,
    observed_rate: Optional[float],
    rating_456: int,
    rating_56: int,
    comment_456: str,
    comment_56: str,
) -> str:
    rate_text = format_observed_rate(num_spins, num_hits)
    return (
        f"総回転数: {num_spins}G\n"
        f"5枚役回数（ヒット数）: {num_hits}回\n"
        f"現在の確率: {rate_text}\n"
        f"456期待度: {prob_456*100:.1f}% (★{rating_456})\n"
        f"56期待度: {prob_56*100:.1f}% (★{rating_56})\n"
        f"コメント(456): {comment_456}\n"
        f"コメント(56): {comment_56}"
    )


def normalize_styles() -> Dict[str, str]:
    return SETTING_COLORS.copy()

