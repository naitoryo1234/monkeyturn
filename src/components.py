from __future__ import annotations

import streamlit as st

from .constants import ACCENT_BLUE, STAR_GOLD
from .logic import normalize_styles


def render_header():
    st.markdown("### スマスロ モンキーターンV 設定判別")
    st.markdown(
        "ベイズ推定で456/56期待度を計算します。総回転数と5枚役回数を入力してください。"
    )


def render_result_card(title: str, probability: float, rating: int, comment: str, extra: str = ""):
    star_fill = "★" * rating + "☆" * (5 - rating)
    st.markdown(
        f"""
        <div class="card">
          <div class="section-title">{title}</div>
          <div style=\"display:flex; align-items:center; justify-content:space-between; margin-bottom:0.35rem;\">
            <div style=\"font-size:1.4rem; font-weight:800;\">{probability*100:.1f}%</div>
            <div class=\"star\">{star_fill}</div>
          </div>
          <div class=\"subtle-text\">{comment}</div>
          {f'<div class="subtle-text" style="margin-top:0.3rem; color:{ACCENT_BLUE};">{extra}</div>' if extra else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_progress(posteriors):
    colors = normalize_styles()
    st.markdown("#### 設定別 確率内訳")
    for setting, prob in sorted(posteriors.items(), key=lambda x: x[0]):
        width = min(max(prob * 100, 0), 100)
        st.markdown(
            f"""
            <div class=\"progress-row\">
              <div class=\"progress-label\">設定{setting}</div>
              <div class=\"progress-track\">
                <div class=\"progress-fill\" style=\"width:{width:.1f}%; background:{colors.get(setting, '#888')};\"></div>
              </div>
              <div style=\"width:52px; text-align:right;\">{prob*100:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_share(text: str):
    st.markdown("#### シェア用テキスト")
    st.text_area("", value=text, height=140)
