PAGE_CSS = """
<style>
html, body, [data-testid=\"stAppViewContainer\"] {
  background: #0f0f0f;
  color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif;
}

main.block-container {
  max-width: 650px;
  padding-top: 1.2rem;
  padding-bottom: 4rem;
}

/* Streamlitボタンの視認性を確保 */
.stButton > button {
  background: linear-gradient(145deg, #1f1f1f, #141414);
  color: #f5f5f5;
  border: 1px solid rgba(58, 155, 220, 0.65);
  border-radius: 10px;
  font-weight: 700;
  padding: 0.5rem 0.9rem;
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}
.stButton > button:hover {
  background: linear-gradient(145deg, #242424, #181818);
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.35);
  transform: translateY(-1px);
}
.stButton > button:active {
  transform: translateY(1px) scale(0.98);
}

.card {
  background: #1a1a1a;
  border-radius: 14px;
  padding: 1rem 1.2rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.section-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: 0.6rem;
}

.quick-btn {
  display: inline-block;
  padding: 0.4rem 0.8rem;
  margin: 0.15rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(145deg, #1f1f1f, #141414);
  color: #f5f5f5;
  font-weight: 700;
  transition: transform 120ms ease, box-shadow 120ms ease, background 120ms ease;
}
.quick-btn:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(0,0,0,0.35); }
.quick-btn:active { transform: translateY(1px) scale(0.98); }

.progress-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 0.4rem;
}
.progress-label { width: 38px; font-weight: 600; color: #ccc; }
.progress-track {
  flex: 1;
  height: 14px;
  border-radius: 999px;
  background: #222;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 200ms ease;
}

.star {
  color: #ffd700;
  text-shadow: 0 0 8px rgba(255, 215, 0, 0.4);
  font-size: 1.05rem;
}
.subtle-text {
  color: #b5b5b5;
  font-size: 0.9rem;
}
</style>
"""
