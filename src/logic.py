from __future__ import annotations

import math
from typing import Dict, Tuple

from .constants import (
    COMMENT_TEMPLATES,
    GOAL_THRESHOLDS,
    PRIOR_PROBS,
    SETTING_COLORS,
    SETTING_PROBS,
    STAGE_BOUNDS,
)


def calculate_likelihood(num_spins: int, num_hits: int, p: float) -> float:
    """二項尤度をログ安定で計算。"""
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
    """事前×尤度を正規化して事後を返却。"""
    if num_spins <= 0:
        return PRIOR_PROBS.copy()

    weighted: Dict[str, float] = {}
    for setting, p in SETTING_PROBS.items():
        likelihood = calculate_likelihood(num_spins, num_hits, p)
        weighted[setting] = PRIOR_PROBS.get(setting, 0.0) * likelihood

    total = sum(weighted.values())
    if total <= 0.0:
        # 安全側のフォールバック
        return PRIOR_PROBS.copy()

    return {k: v / total for k, v in weighted.items()}


def summarize(num_spins: int, num_hits: int) -> Dict[str, float]:
    posteriors = compute_posteriors(num_spins, num_hits)
    prob_456 = sum(posteriors.get(s, 0.0) for s in ("4", "5", "6"))
    prob_56 = sum(posteriors.get(s, 0.0) for s in ("5", "6"))
    observed_rate = (num_spins / num_hits) if num_hits > 0 else None
    return {
        "posteriors": posteriors,
        "prob_456": prob_456,
        "prob_56": prob_56,
        "observed_rate": observed_rate,
    }


def evaluate_goal(goal_code: str, goal_prob: float, alt_prob: float, sample_n: int) -> Tuple[int, str]:
    """
    456/56向けの星数評価を返す。
    戻り値: (rating 1-5, 状態タグ)
    """
    th = GOAL_THRESHOLDS[goal_code]
    diff = goal_prob - alt_prob

    if sample_n < th["min_sample"]:
        return 1, "sample_low"

    if goal_prob >= th["high_goal"] or diff >= th["high_diff"]:
        # かなり優勢
        if goal_prob >= th["high_goal"] + 0.08 or diff >= th["high_diff"] * 1.3:
            return 5, "high"
        return 4, "high"

    if goal_prob >= th["mid_goal"] or diff >= th["mid_diff"]:
        return 3, "mid"

    if goal_prob < th["low_goal"]:
        return 1 if diff < 0 else 2, "low"

    return 2, "low"


def stage_from_sample(sample_n: int) -> str:
    if sample_n < STAGE_BOUNDS["early"]:
        return "early"
    if sample_n < STAGE_BOUNDS["mid"]:
        return "mid"
    return "late"


def build_comment(sample_n: int, rating: int) -> str:
    stage = stage_from_sample(sample_n)
    bucket = COMMENT_TEMPLATES.get(stage, {})
    phrases = bucket.get(rating) or bucket.get(3) or [""]
    return " ".join(phrases[:2]).strip()


def build_share_text(
    num_spins: int,
    num_hits: int,
    prob_456: float,
    prob_56: float,
    observed_rate: float | None,
    rating_456: int,
    rating_56: int,
    comment_456: str,
    comment_56: str,
) -> str:
    rate_text = f"1/{observed_rate:.1f}" if observed_rate else "データ不足"
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
    """設定別カラーをまとめて返す（UI用）。"""
    return SETTING_COLORS.copy()
