from __future__ import annotations

import streamlit as st

from src.components import render_progress, render_result_card, render_share
from src.constants import GOAL_THRESHOLDS
from src.logic import (
    build_alignment_comment,
    build_comment,
    build_share_text,
    evaluate_goal,
    format_observed_rate,
    summarize,
)
from src.styles import PAGE_CSS

st.set_page_config(page_title="スマスロ モンキーターンV 設定判別", page_icon="🎰", layout="centered")
st.markdown(PAGE_CSS, unsafe_allow_html=True)

# セッション初期化
for key, default in {
    "num_spins_input": 0,
    "num_hits_input": 0,
    "calc_spins": None,
    "calc_hits": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def add_spins(delta: int):
    st.session_state.num_spins_input = max(0, st.session_state.num_spins_input + delta)


def add_hits(delta: int):
    st.session_state.num_hits_input = max(0, st.session_state.num_hits_input + delta)


def commit_values():
    st.session_state.calc_spins = int(max(0, st.session_state.num_spins_input))
    st.session_state.calc_hits = int(max(0, st.session_state.num_hits_input))


def reset_values():
    st.session_state.num_spins_input = 0
    st.session_state.num_hits_input = 0
    st.session_state.calc_spins = None
    st.session_state.calc_hits = None


with st.container():
    col_spins, col_hits = st.columns(2)
    with col_spins:
        st.number_input("総回転数 (G)", min_value=0, step=10, key="num_spins_input")
        btns = st.columns(4)
        for idx, val in enumerate([50, 100, 500, 1000]):
            btns[idx].button(f"+{val}", key=f"spin_{val}", on_click=add_spins, args=(val,))
    with col_hits:
        st.number_input("5枚役回数（ヒット数）", min_value=0, step=1, key="num_hits_input")
        btns_h = st.columns(4)
        for idx, val in enumerate([1, 5, 10, 20]):
            btns_h[idx].button(f"+{val}", key=f"hit_{val}", on_click=add_hits, args=(val,))

    c1, c2 = st.columns(2)
    c1.button("判別する", type="primary", on_click=commit_values)
    c2.button("リセット", on_click=reset_values)

calc_spins = st.session_state.calc_spins
calc_hits = st.session_state.calc_hits

has_result = calc_spins is not None and calc_hits is not None

if has_result:
    result = summarize(calc_spins, calc_hits)
    posteriors = result["posteriors"]
    prob_456 = result["prob_456"]
    prob_56 = result["prob_56"]
    observed_rate = result["observed_rate"]

    rating_456, tag_456 = evaluate_goal("456", prob_456, 1 - prob_456, calc_spins)
    rating_56, tag_56 = evaluate_goal("56", prob_56, 1 - prob_56, calc_spins)

    comment_456 = build_comment("456", prob_456, 1 - prob_456, calc_spins, rating_456, tag_456)
    comment_56 = build_comment("56", prob_56, 1 - prob_56, calc_spins, rating_56, tag_56)

    alignment_note = build_alignment_comment(prob_456, prob_56)

    extra_456 = ""
    extra_56 = ""
    if calc_spins < GOAL_THRESHOLDS["456"]["min_sample"]:
        extra_456 = f"サンプルが少ないため信頼度低め（推奨 {GOAL_THRESHOLDS['456']['recommended_sample']}G）"
    if calc_spins < GOAL_THRESHOLDS["56"]["min_sample"]:
        extra_56 = f"サンプルが少ないため信頼度低め（推奨 {GOAL_THRESHOLDS['56']['recommended_sample']}G）"

    if alignment_note:
        extra_56 = f"{extra_56 + ' / ' if extra_56 else ''}{alignment_note}"

    rate_text = format_observed_rate(calc_spins, calc_hits)

    st.markdown("#### 入力サマリー")
    st.markdown(
        f"""
        <div class=\"summary-row\">
          <div class=\"summary-item\">
            <div class=\"summary-label\">総回転数</div>
            <div class=\"summary-value\">{calc_spins}G</div>
          </div>
          <div class=\"summary-item\">
            <div class=\"summary-label\">5枚役回数（ヒット数）</div>
            <div class=\"summary-value\">{calc_hits}回</div>
          </div>
          <div class=\"summary-item\">
            <div class=\"summary-label\">実測確率</div>
            <div class=\"summary-value\">{rate_text}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
        render_result_card("456期待度", prob_456, rating_456, comment_456, extra_456)
    with col_b:
        render_result_card("56期待度", prob_56, rating_56, comment_56, extra_56)

    st.markdown("---")

    render_progress(posteriors)

    share_text = build_share_text(
        calc_spins,
        calc_hits,
        prob_456,
        prob_56,
        observed_rate,
        rating_456,
        rating_56,
        comment_456,
        comment_56,
    )
    render_share(share_text)
else:
    st.info("入力後に『判別する』ボタンを押してください。")