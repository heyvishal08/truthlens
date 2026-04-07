import streamlit as st
import requests
import time

st.set_page_config(
    page_title="TruthLens — Fake News Detector",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    background: #080810 !important;
    color: #e8e8f0 !important;
    font-family: 'Outfit', sans-serif !important;
}

.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Animated background ── */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 50% at 20% 20%, rgba(255,200,0,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(255,50,80,0.04) 0%, transparent 60%),
        radial-gradient(ellipse 50% 60% at 50% 50%, rgba(0,150,255,0.02) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    animation: bgShift 15s ease-in-out infinite alternate;
}

@keyframes bgShift {
    0%   { opacity: 0.6; }
    100% { opacity: 1; }
}

/* ── Scanline effect ── */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(255,255,255,0.008) 2px,
        rgba(255,255,255,0.008) 4px
    );
    pointer-events: none;
    z-index: 0;
}

/* ── Main wrapper ── */
.main-wrapper {
    position: relative;
    z-index: 1;
    max-width: 900px;
    margin: 0 auto;
    padding: 48px 24px 100px;
}

/* ── Header ── */
.site-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 64px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.logo-wrap {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo-mark {
    width: 44px; height: 44px;
    background: #ffc800;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 0 30px rgba(255,200,0,0.3);
}

.logo-name {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    letter-spacing: 3px;
    color: #fff;
}

.logo-name span { color: #ffc800; }

.version-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: rgba(255,255,255,0.3);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 1px;
}

/* ── Hero ── */
.hero-section {
    text-align: center;
    margin-bottom: 52px;
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #ffc800;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 20px;
    padding: 6px 16px;
    background: rgba(255,200,0,0.08);
    border: 1px solid rgba(255,200,0,0.2);
    border-radius: 99px;
}

.hero-eyebrow::before {
    content: '';
    width: 6px; height: 6px;
    background: #ffc800;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}

.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(52px, 10vw, 96px);
    line-height: 0.95;
    letter-spacing: 4px;
    color: #fff;
    margin-bottom: 20px;
}

.hero-title .accent { color: #ffc800; }
.hero-title .dim { color: rgba(255,255,255,0.2); }

.hero-sub {
    font-size: 16px;
    font-weight: 300;
    color: rgba(255,255,255,0.4);
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.7;
    letter-spacing: 0.2px;
}

/* ── Stats bar ── */
.stats-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 40px;
    margin-bottom: 48px;
    padding: 20px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
}

.stat-item {
    text-align: center;
}

.stat-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    letter-spacing: 2px;
    color: #ffc800;
    line-height: 1;
}

.stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

.stat-divider {
    width: 1px;
    height: 32px;
    background: rgba(255,255,255,0.08);
}

/* ── Sample pills ── */
.sample-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

/* ── Input zone ── */
.input-zone {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 20px;
    transition: border-color 0.3s;
}

.input-zone:focus-within {
    border-color: rgba(255,200,0,0.25);
    box-shadow: 0 0 0 1px rgba(255,200,0,0.08), 0 20px 60px rgba(0,0,0,0.5);
}

.input-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 2px;
    text-transform: uppercase;
}

.input-dot {
    width: 6px; height: 6px;
    background: #ffc800;
    border-radius: 50%;
}

/* Override Streamlit textarea */
.stTextArea textarea {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 14px !important;
    color: #e8e8f0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 15px !important;
    font-weight: 300 !important;
    line-height: 1.7 !important;
    padding: 16px !important;
    resize: vertical !important;
    transition: border-color 0.2s !important;
}

.stTextArea textarea:focus {
    border-color: rgba(255,200,0,0.3) !important;
    box-shadow: none !important;
    outline: none !important;
}

.stTextArea textarea::placeholder {
    color: rgba(255,255,255,0.2) !important;
}

.stTextArea label { display: none !important; }

/* ── Buttons ── */
.stButton > button {
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 2px !important;
    border-radius: 12px !important;
    border: none !important;
    transition: all 0.2s !important;
    font-size: 16px !important;
}

/* Main analyze button */
div[data-testid="column"]:has(> div > div > div > button.analyze-btn) > div > div > div > button,
.analyze-btn-wrap .stButton > button {
    background: #ffc800 !important;
    color: #080810 !important;
    padding: 16px 40px !important;
    width: 100% !important;
    font-size: 18px !important;
}

/* Sample buttons */
.sample-fake .stButton > button {
    background: rgba(255,50,80,0.1) !important;
    color: #ff3250 !important;
    border: 1px solid rgba(255,50,80,0.2) !important;
    font-size: 12px !important;
    padding: 8px 16px !important;
    width: 100% !important;
}

.sample-real .stButton > button {
    background: rgba(0,220,130,0.1) !important;
    color: #00dc82 !important;
    border: 1px solid rgba(0,220,130,0.2) !important;
    font-size: 12px !important;
    padding: 8px 16px !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    filter: brightness(1.1) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* ── Result cards ── */
.verdict-card {
    border-radius: 24px;
    padding: 36px;
    margin: 28px 0 20px;
    position: relative;
    overflow: hidden;
    border: 1px solid transparent;
    animation: revealUp 0.5s ease both;
}

@keyframes revealUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}

.verdict-fake {
    background: linear-gradient(135deg, rgba(255,30,60,0.08) 0%, rgba(255,30,60,0.03) 100%);
    border-color: rgba(255,30,60,0.25);
}

.verdict-real {
    background: linear-gradient(135deg, rgba(0,220,130,0.08) 0%, rgba(0,220,130,0.03) 100%);
    border-color: rgba(0,220,130,0.25);
}

.verdict-uncertain {
    background: linear-gradient(135deg, rgba(255,180,0,0.08) 0%, rgba(255,180,0,0.03) 100%);
    border-color: rgba(255,180,0,0.25);
}

.verdict-glow {
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.15;
}

.verdict-fake .verdict-glow   { background: #ff1e3c; }
.verdict-real .verdict-glow   { background: #00dc82; }
.verdict-uncertain .verdict-glow { background: #ffb400; }

.verdict-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 24px;
}

.verdict-icon-wrap {
    font-size: 48px;
    line-height: 1;
}

.verdict-text { flex: 1; }

.verdict-label {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 52px;
    letter-spacing: 4px;
    line-height: 1;
    margin-bottom: 6px;
}

.verdict-fake .verdict-label   { color: #ff1e3c; }
.verdict-real .verdict-label   { color: #00dc82; }
.verdict-uncertain .verdict-label { color: #ffb400; }

.verdict-desc {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: rgba(255,255,255,0.35);
    letter-spacing: 0.5px;
}

.confidence-pill {
    text-align: center;
    padding: 16px 24px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    min-width: 110px;
    flex-shrink: 0;
}

.conf-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 44px;
    letter-spacing: -1px;
    line-height: 1;
}

.verdict-fake .conf-num   { color: #ff1e3c; }
.verdict-real .conf-num   { color: #00dc82; }
.verdict-uncertain .conf-num { color: #ffb400; }

.conf-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 2px;
}

/* Progress bar */
.prog-wrap { margin-bottom: 4px; }
.prog-label {
    display: flex;
    justify-content: space-between;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: rgba(255,255,255,0.25);
    margin-bottom: 6px;
}

.prog-track {
    height: 4px;
    background: rgba(255,255,255,0.06);
    border-radius: 99px;
    overflow: hidden;
}

.prog-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 1.2s cubic-bezier(0.34,1.56,0.64,1);
}

.verdict-fake .prog-fill   { background: linear-gradient(90deg, #ff1e3c, #ff6b81); }
.verdict-real .prog-fill   { background: linear-gradient(90deg, #00dc82, #00ffaa); }
.verdict-uncertain .prog-fill { background: linear-gradient(90deg, #ffb400, #ffd060); }

/* ── Metrics grid ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 20px 0;
}

.metric-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 18px;
    text-align: center;
}

.metric-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 32px;
    letter-spacing: 1px;
    line-height: 1;
}

.metric-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── Signal panel ── */
.signal-panel {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 20px;
    margin-top: 16px;
}

.signal-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: rgba(255,255,255,0.3);
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.signal-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}

.signal-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

.signal-row:last-child { border-bottom: none; }

.signal-left {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
    color: rgba(255,255,255,0.7);
}

.signal-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-high    { background: #ff1e3c; box-shadow: 0 0 6px rgba(255,30,60,0.5); }
.dot-medium  { background: #ffb400; box-shadow: 0 0 6px rgba(255,180,0,0.5); }
.dot-low     { background: #00dc82; box-shadow: 0 0 6px rgba(0,220,130,0.5); }

.signal-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: rgba(255,255,255,0.3);
    margin-left: 8px;
}

.signal-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    padding: 3px 10px;
    border-radius: 99px;
    letter-spacing: 1px;
}

.badge-high   { background: rgba(255,30,60,0.12);  color: #ff1e3c; border: 1px solid rgba(255,30,60,0.2); }
.badge-medium { background: rgba(255,180,0,0.12);  color: #ffb400; border: 1px solid rgba(255,180,0,0.2); }
.badge-low    { background: rgba(0,220,130,0.12);  color: #00dc82; border: 1px solid rgba(0,220,130,0.2); }

/* ── How it works ── */
.how-section {
    margin-top: 60px;
}

.section-head {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 32px;
    letter-spacing: 3px;
    color: rgba(255,255,255,0.15);
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.section-head::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.05);
}

.steps-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

.step-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 20px 16px;
    transition: border-color 0.2s;
}

.step-card:hover {
    border-color: rgba(255,200,0,0.15);
}

.step-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 36px;
    letter-spacing: 2px;
    color: rgba(255,200,0,0.2);
    line-height: 1;
    margin-bottom: 10px;
}

.step-name {
    font-size: 13px;
    font-weight: 600;
    color: rgba(255,255,255,0.7);
    margin-bottom: 6px;
}

.step-desc {
    font-size: 11px;
    color: rgba(255,255,255,0.3);
    line-height: 1.6;
}

/* ── Stack chips ── */
.stack-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 20px;
}

.chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    padding: 5px 12px;
    border-radius: 99px;
    border: 1px solid rgba(255,255,255,0.08);
    color: rgba(255,255,255,0.3);
    letter-spacing: 0.5px;
}

.chip-accent {
    border-color: rgba(255,200,0,0.2);
    color: rgba(255,200,0,0.7);
    background: rgba(255,200,0,0.05);
}

/* ── Footer ── */
.site-footer {
    margin-top: 60px;
    padding-top: 24px;
    border-top: 1px solid rgba(255,255,255,0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.footer-left {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: rgba(255,255,255,0.2);
}

.footer-right {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: rgba(255,255,255,0.2);
}

/* Streamlit overrides */
div[data-testid="stVerticalBlock"] { gap: 0 !important; }
.stSpinner > div { border-color: #ffc800 transparent transparent transparent !important; }
[data-testid="stMarkdownContainer"] p { margin: 0; }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000/predict"

SAMPLES = {
    "fake1": "SHOCKING: Scientists CONFIRM that drinking lemon juice cures ALL cancers overnight! Big Pharma desperately hiding this miracle cure from the public. Share before it gets deleted!!!",
    "fake2": "BREAKING: The moon landing was STAGED in a Hollywood studio! Leaked NASA documents CONFIRM what conspiracy theorists have known for years. Government has been LYING to us for decades!!!",
    "real1": "The Intergovernmental Panel on Climate Change released its assessment report, indicating that global temperatures have risen 1.1 degrees Celsius above pre-industrial levels, compiled by over 230 scientists.",
    "real2": "Apple reported quarterly revenue of $89.5 billion, with its services segment growing 16 percent year-over-year according to the company's official earnings call on Tuesday."
}

# ── Layout ──────────────────────────────────────────────────
st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="site-header">
    <div class="logo-wrap">
        <div class="logo-mark">🔍</div>
        <div class="logo-name">TRUTH<span>LENS</span></div>
    </div>
    <div class="version-tag">v1.0 · PORTFOLIO PROJECT</div>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero-section">
    <div class="hero-eyebrow">AI-Powered Detection</div>
    <div class="hero-title">
        DETECT<br>
        <span class="accent">FAKE</span> <span class="dim">/</span> REAL<br>
        NEWS
    </div>
    <p class="hero-sub">Fine-tuned DistilBERT model trained on 70,000+ articles. Paste any headline or article to instantly analyze it for misinformation signals.</p>
</div>
""", unsafe_allow_html=True)

# Stats bar
st.markdown("""
<div class="stats-bar">
    <div class="stat-item">
        <div class="stat-num">98.9%</div>
        <div class="stat-label">Accuracy</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-num">70K+</div>
        <div class="stat-label">Training Articles</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-num">0.989</div>
        <div class="stat-label">F1 Score</div>
    </div>
    <div class="stat-divider"></div>
    <div class="stat-item">
        <div class="stat-num">&lt;1s</div>
        <div class="stat-label">Inference Time</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sample buttons
st.markdown('<div class="sample-label">Try a sample →</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown('<div class="sample-fake">', unsafe_allow_html=True)
    if st.button("🚨 Fake Sample 1"):
        st.session_state.text = SAMPLES["fake1"]
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="sample-fake">', unsafe_allow_html=True)
    if st.button("🚨 Fake Sample 2"):
        st.session_state.text = SAMPLES["fake2"]
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="sample-real">', unsafe_allow_html=True)
    if st.button("✅ Real Sample 1"):
        st.session_state.text = SAMPLES["real1"]
    st.markdown('</div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="sample-real">', unsafe_allow_html=True)
    if st.button("✅ Real Sample 2"):
        st.session_state.text = SAMPLES["real2"]
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# Input area
st.markdown("""
<div class="input-header">
    <div class="input-dot"></div>
    NEWS INPUT
</div>
""", unsafe_allow_html=True)

text_input = st.text_area(
    "input",
    value=st.session_state.get('text', ''),
    height=160,
    placeholder="Paste any news article, headline, or suspicious text here...\n\nExample: 'BREAKING: Scientists confirm miracle cure hidden by Big Pharma...'"
)

char_color = "rgba(255,200,0,0.6)" if len(text_input) > 0 else "rgba(255,255,255,0.2)"
st.markdown(f"<p style='font-family:JetBrains Mono,monospace;font-size:11px;color:{char_color};margin-top:8px;letter-spacing:1px;'>{len(text_input)} CHARACTERS</p>", unsafe_allow_html=True)

st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# Analyze button
col_btn, col_space = st.columns([1, 2])
with col_btn:
    analyze = st.button("⚡  ANALYZE NOW", use_container_width=True)

# ── Prediction ───────────────────────────────────────────────
if analyze:
    if not text_input.strip():
        st.markdown("""
        <div style='background:rgba(255,30,60,0.08);border:1px solid rgba(255,30,60,0.2);
             border-radius:12px;padding:14px 18px;margin-top:16px;
             font-family:JetBrains Mono,monospace;font-size:12px;color:#ff1e3c;'>
            ⚠ Please enter some text to analyze.
        </div>""", unsafe_allow_html=True)
    else:
        with st.spinner("Analyzing with DistilBERT..."):
            try:
                response = requests.post(API_URL, json={"text": text_input}, timeout=30)

                if response.status_code == 200:
                    r = response.json()
                    label      = r['label']
                    confidence = r['confidence']
                    fake_prob  = r['fake_prob']
                    real_prob  = r['real_prob']
                    risk_score = r['risk_score']
                    signals    = r['signals']

                    # Determine styles
                    if label == "FAKE":
                        vc = "verdict-fake"
                        icon = "⚠️"
                        verdict_text = "LIKELY FAKE"
                        desc = "High probability of misinformation detected"
                        metric_color = "#ff1e3c"
                    elif label == "REAL":
                        vc = "verdict-real"
                        icon = "✅"
                        verdict_text = "LIKELY REAL"
                        desc = "Low misinformation indicators detected"
                        metric_color = "#00dc82"
                    else:
                        vc = "verdict-uncertain"
                        icon = "🔍"
                        verdict_text = "UNCERTAIN"
                        desc = "Mixed signals — verify with trusted sources"
                        metric_color = "#ffb400"

                    # Verdict card
                    st.markdown(f"""
                    <div class="verdict-card {vc}">
                        <div class="verdict-glow"></div>
                        <div class="verdict-top">
                            <div class="verdict-text">
                                <div style="font-size:48px;line-height:1;margin-bottom:8px;">{icon}</div>
                                <div class="verdict-label">{verdict_text}</div>
                                <div class="verdict-desc">{desc}</div>
                            </div>
                            <div class="confidence-pill">
                                <div class="conf-num">{confidence:.0f}<span style="font-size:20px;">%</span></div>
                                <div class="conf-label">Confidence</div>
                            </div>
                        </div>
                        <div class="prog-wrap">
                            <div class="prog-label">
                                <span>RISK LEVEL</span>
                                <span>{risk_score}/100</span>
                            </div>
                            <div class="prog-track">
                                <div class="prog-fill" style="width:{risk_score}%"></div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Metrics grid
                    st.markdown(f"""
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-val" style="color:{metric_color};">{confidence:.1f}%</div>
                            <div class="metric-lbl">Confidence</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-val" style="color:#ff1e3c;">{fake_prob:.1f}%</div>
                            <div class="metric-lbl">Fake Probability</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-val" style="color:#00dc82;">{real_prob:.1f}%</div>
                            <div class="metric-lbl">Real Probability</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Signal breakdown
                    signal_rows = ""
                    for s in signals:
                        risk = s['risk'].upper()
                        if risk == 'HIGH':
                            dot_class = "dot-high"
                            badge_class = "badge-high"
                        elif risk in ('MEDIUM', 'MED'):
                            dot_class = "dot-medium"
                            badge_class = "badge-medium"
                        else:
                            dot_class = "dot-low"
                            badge_class = "badge-low"

                        signal_rows += f"""
                        <div class="signal-row">
                            <div class="signal-left">
                                <div class="signal-dot {dot_class}"></div>
                                {s['name']}
                                <span class="signal-val">{s['value']}</span>
                            </div>
                            <span class="signal-badge {badge_class}">{risk}</span>
                        </div>"""

                    st.markdown(f"""
                    <div class="signal-panel">
                        <div class="signal-title">Signal Breakdown</div>
                        {signal_rows}
                    </div>
                    """, unsafe_allow_html=True)

                else:
                    st.error(f"API error: {response.status_code}")

            except requests.exceptions.ConnectionError:
                st.markdown("""
                <div style='background:rgba(255,30,60,0.08);border:1px solid rgba(255,30,60,0.2);
                     border-radius:14px;padding:20px;margin-top:16px;font-family:JetBrains Mono,monospace;font-size:12px;color:#ff1e3c;'>
                    ⚠ Cannot connect to API.<br><br>
                    Make sure Terminal 1 is running:<br>
                    <span style="color:rgba(255,255,255,0.4);">python -m uvicorn api.main:app --reload</span>
                </div>""", unsafe_allow_html=True)

# ── How it works ─────────────────────────────────────────────
st.markdown("""
<div class="how-section">
    <div class="section-head">HOW IT WORKS</div>
    <div class="steps-row">
        <div class="step-card">
            <div class="step-num">01</div>
            <div class="step-name">Tokenization</div>
            <div class="step-desc">Text split into subword tokens using DistilBERT tokenizer, max 256 tokens.</div>
        </div>
        <div class="step-card">
            <div class="step-num">02</div>
            <div class="step-name">Embedding</div>
            <div class="step-desc">Tokens converted to 768-dim contextual embeddings capturing semantic meaning.</div>
        </div>
        <div class="step-card">
            <div class="step-num">03</div>
            <div class="step-name">Classification</div>
            <div class="step-desc">Fine-tuned classifier head outputs FAKE/REAL probabilities via softmax.</div>
        </div>
        <div class="step-card">
            <div class="step-num">04</div>
            <div class="step-name">Signal Analysis</div>
            <div class="step-desc">Rule-based heuristics score linguistic patterns on top of model output.</div>
        </div>
    </div>
    <div class="stack-row">
        <span class="chip chip-accent">DistilBERT</span>
        <span class="chip chip-accent">HuggingFace</span>
        <span class="chip chip-accent">FastAPI</span>
        <span class="chip chip-accent">Streamlit</span>
        <span class="chip">PyTorch</span>
        <span class="chip">WELFake Dataset</span>
        <span class="chip">SHAP</span>
        <span class="chip">Scikit-learn</span>
        <span class="chip">Python 3.12</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="site-footer">
    <div class="footer-left">TRUTHLENS v1.0 · BUILT BY VISHAL · PORTFOLIO PROJECT #1</div>
    <div class="footer-right">DISTILBERT · WELFAKE · 98.9% ACCURACY</div>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
