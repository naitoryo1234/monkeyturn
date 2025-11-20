from __future__ import annotations

import streamlit as st

from src.components import render_header, render_progress, render_result_card, render_share
from src.constants import GOAL_THRESHOLDS
from src.logic import build_comment, build_share_text, evaluate_goal, summarize
from src.styles import PAGE_CSS

st.set_page_config(page_title="スマスロ モンキーターンV 設定判別", page_icon="🎰", layout="centered")
st.markdown(PAGE_CSS, unsafe_allow_html=True)

if "num_spins" not in st.session_state:
    st.session_state.num_spins = 0
if "num_hits" not in st.session_state:
    st.session_state.num_hits = 0


def update_value(key: str, delta: int):
    current = st.session_state.get(key, 0)
    new_val = max(0, current + delta)
    st.session_state[key] = new_val
    st.rerun()


def reset_values():
    st.session_state.num_spins = 0
    st.session_state.num_hits = 0
    st.rerun()


render_header()

with st.container():
    st.markdown("#### 入力")
    col_spins, col_hits = st.columns(2)
    with col_spins:
        spins = st.number_input("総回転数 (G)", min_value=0, value=st.session_state.num_spins, step=10)
        if spins != st.session_state.num_spins:
            st.session_state.num_spins = int(spins)
        btns = st.columns(4)
        for idx, val in enumerate([50, 100, 500, 1000]):
            if btns[idx].button(f"+{val}", key=f"spin_{val}"):
                update_value("num_spins", val)
    with col_hits:
        hits = st.number_input("5枚役回数（ヒット数）", min_value=0, value=st.session_state.num_hits, step=1)
        if hits != st.session_state.num_hits:
            st.session_state.num_hits = int(hits)
        btns_h = st.columns(4)
        for idx, val in enumerate([1, 5, 10, 20]):
            if btns_h[idx].button(f"+{val}", key=f"hit_{val}"):
                update_value("num_hits", val)

    reset_col = st.columns(3)[2]
    if reset_col.button("リセット", type="primary"):
        reset_values()

# ボタン操作後に最新を取得
num_spins = st.session_state.num_spins
num_hits = st.session_state.num_hits

result = summarize(num_spins, num_hits)
posteriors = result["posteriors"]
prob_456 = result["prob_456"]
prob_56 = result["prob_56"]
observed_rate = result["observed_rate"]

rating_456, _ = evaluate_goal("456", prob_456, 1 - prob_456, num_spins)
rating_56, _ = evaluate_goal("56", prob_56, 1 - prob_56, num_spins)

comment_456 = build_comment(num_spins, rating_456)
comment_56 = build_comment(num_spins, rating_56)

extra_456 = ""
extra_56 = ""
if num_spins < GOAL_THRESHOLDS["456"]["min_sample"]:
    extra_456 = f"サンプルが少ないため信頼度低め（推奨 {GOAL_THRESHOLDS['456']['recommended_sample']}G）"
if num_spins < GOAL_THRESHOLDS["56"]["min_sample"]:
    extra_56 = f"サンプルが少ないため信頼度低め（推奨 {GOAL_THRESHOLDS['56']['recommended_sample']}G）"

col_a, col_b = st.columns(2)
with col_a:
    render_result_card("456期待度", prob_456, rating_456, comment_456, extra_456)
with col_b:
    render_result_card("56期待度", prob_56, rating_56, comment_56, extra_56)

st.markdown("---")

rate_text = f"1/{observed_rate:.1f}" if observed_rate else "--"
st.metric("現在の確率 (実測)", rate_text, help="総回転数 / 5枚役回数")

render_progress(posteriors)

share_text = build_share_text(
    num_spins,
    num_hits,
    prob_456,
    prob_56,
    observed_rate,
    rating_456,
    rating_56,
    comment_456,
    comment_56,
)
render_share(share_text)

st.caption("streamlit run main.py で起動できます。")
