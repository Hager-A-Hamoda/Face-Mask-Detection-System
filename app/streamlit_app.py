import streamlit as st
import requests
import io
import os
from PIL import Image

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MaskScan",
    page_icon="⬡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

API_URL = os.getenv("API_URL", "http://localhost:8000/predict")

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #f7f9fc;
    --surface:   #ffffff;
    --surface-2: #f0f4f9;
    --border:    #dce6f2;

    --primary:   #5b8def;
    --primary-soft: #dbe7ff;

    --green:     #43b581;
    --green-soft:#dff6eb;

    --red:       #ef6b73;
    --red-soft:  #ffe4e6;

    --text:      #24324a;
    --muted:     #7b8aa0;

    --shadow:    0 10px 30px rgba(91,141,239,0.08);

    --mono:      'DM Mono', monospace;
    --sans:      'Syne', sans-serif;
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background: linear-gradient(to bottom right, #f7f9fc, #edf4ff) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

#MainMenu,
footer,
[data-testid="stToolbar"] {
    display: none !important;
}

/* ── Layout ── */
[data-testid="stMainBlockContainer"] {
    max-width: 720px !important;
    margin: 0 auto !important;
}

.block-container {
    padding: 2rem 1.5rem 4rem !important;
}

/* ── Header ── */
.ms-header {
    padding: 2rem 0 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
}

.ms-logo {
    font-family: var(--sans);
    font-size: 1rem;
    font-weight: 700;
    color: var(--primary);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}

.ms-title {
    font-family: var(--sans);
    font-size: clamp(2.6rem, 6vw, 4rem);
    font-weight: 800;
    line-height: 1.05;
    margin: 0.7rem 0;
    color: var(--text);
}

.ms-subtitle {
    font-size: 0.82rem;
    color: var(--muted);
    letter-spacing: 0.04em;
}

/* ── Tabs ── */
[data-testid="stTabs"] {
    margin-bottom: 2rem;
}

[data-testid="stTabs"] > div:first-child {
    gap: 0.5rem;
    border-bottom: none !important;
}

button[data-baseweb="tab"] {
    background: var(--surface) !important;
    border: 1px solid transparent !important;
    border-radius: 12px !important;

    color: var(--muted) !important;

    padding: 0.7rem 1.3rem !important;

    font-family: var(--mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;

    transition: all 0.2s ease !important;
}

button[data-baseweb="tab"]:hover {
    background: var(--surface-2) !important;
    color: var(--text) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: var(--primary-soft) !important;
    color: var(--primary) !important;
    border: 1px solid rgba(91,141,239,0.2) !important;
}

/* ── Upload box ── */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 18px !important;

    padding: 2rem !important;

    box-shadow: var(--shadow);
    transition: all 0.2s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
    transform: translateY(-1px);
}

[data-testid="stFileUploader"] label {
    color: var(--muted) !important;
    font-size: 0.82rem !important;
}

[data-testid="stFileUploader"] small {
    color: var(--muted) !important;
}

/* ── Image ── */
[data-testid="stImage"] img {
    border-radius: 18px !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow);
}

/* ── Camera ── */
[data-testid="stCameraInput"] video,
[data-testid="stCameraInput"] canvas {
    border-radius: 18px !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow);
}

[data-testid="stCameraInput"] button {
    background: var(--primary-soft) !important;
    color: var(--primary) !important;

    border: none !important;
    border-radius: 12px !important;

    padding: 0.7rem 1rem !important;

    font-family: var(--mono) !important;
    font-size: 0.72rem !important;

    transition: all 0.2s ease !important;
}

[data-testid="stCameraInput"] button:hover {
    transform: translateY(-1px);
}

/* ── Result card ── */
.ms-result {
    margin-top: 1.7rem;

    background: var(--surface);
    border: 1px solid var(--border);

    border-radius: 20px;
    overflow: hidden;

    box-shadow: var(--shadow);
}

.ms-result-header {
    display: flex;
    align-items: center;
    gap: 1rem;

    padding: 1.1rem 1.4rem;

    background: rgba(255,255,255,0.7);
    border-bottom: 1px solid var(--border);
}

.ms-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;

    padding: 0.4rem 0.8rem;

    border-radius: 999px;

    font-size: 0.68rem;
    font-weight: 600;

    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.ms-badge-allow {
    background: var(--green-soft);
    color: var(--green);
}

.ms-badge-deny {
    background: var(--red-soft);
    color: var(--red);
}

.ms-result-label {
    font-family: var(--sans);
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    flex: 1;
}

.ms-result-conf {
    color: var(--muted);
    font-size: 0.75rem;
}

.ms-result-body {
    padding: 1.2rem 1.4rem;
}

.ms-row {
    display: flex;
    justify-content: space-between;

    padding: 0.55rem 0;

    border-bottom: 1px solid #eef2f7;
}

.ms-row:last-child {
    border-bottom: none;
}

.ms-row-key {
    color: var(--muted);
    font-size: 0.74rem;
    letter-spacing: 0.04em;
}

.ms-row-val {
    color: var(--text);
    font-size: 0.78rem;
    font-weight: 500;
}

/* ── Confidence bar ── */
.ms-bar-wrap {
    margin-top: 1rem;

    height: 8px;

    background: #edf2f7;
    border-radius: 999px;

    overflow: hidden;
}

.ms-bar-fill {
    height: 100%;
    border-radius: 999px;

    transition: width 0.5s ease;
}

.ms-bar-fill-allow {
    background: linear-gradient(to right, #43b581, #70d6a6);
}

.ms-bar-fill-deny {
    background: linear-gradient(to right, #ef6b73, #ff9aa2);
}

/* ── Spinner ── */
[data-testid="stSpinner"] {
    color: var(--muted) !important;
    font-size: 0.78rem !important;
}

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;

    border-radius: 16px !important;

    color: var(--text) !important;
}

/* ── Footer ── */
.ms-footer {
    margin-top: 4rem;
    padding-top: 1.5rem;

    text-align: center;

    color: var(--muted);
    font-size: 0.72rem;
}

.ms-dot {
    display: inline-block;

    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: var(--green);

    margin-right: 0.4rem;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ms-header">
    <div class="ms-logo">⬡ MaskScan</div>
    <div class="ms-title">Face Mask<br>Detection</div>
    <div class="ms-subtitle">MobileNetV2 · transfer learning · 2-class classifier</div>
</div>
""", unsafe_allow_html=True)


# ── Helper: call API and render result ────────────────────────────────────────
def call_api(img: Image.Image):
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    with st.spinner("running inference …"):
        try:
            resp = requests.post(API_URL, files={"file": ("image.jpg", buf, "image/jpeg")}, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError:
            st.error("Cannot reach API — is the backend running?")
        except requests.exceptions.HTTPError as e:
            st.error(f"API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
    return None


def render_result(result: dict):
    cls        = result.get("class", "Unknown")
    status     = result.get("status", "")
    confidence = result.get("confidence", 0.0)
    action     = result.get("action", "")
    all_probs  = result.get("all_probabilities", {})

    is_allow   = status == "mask_on"
    badge_cls  = "ms-badge-allow" if is_allow else "ms-badge-deny"
    bar_cls    = "ms-bar-fill-allow" if is_allow else "ms-bar-fill-deny"
    dot        = "●"

    prob_rows = "".join(
        f'<div class="ms-row"><span class="ms-row-key">{k}</span>'
        f'<span class="ms-row-val">{v:.1%}</span></div>'
        for k, v in all_probs.items()
    )

    st.markdown(f"""
    <div class="ms-result">
        <div class="ms-result-header">
            <span class="ms-badge {badge_cls}">{dot} {action}</span>
            <span class="ms-result-label">{cls}</span>
            <span class="ms-result-conf">{confidence:.1%}</span>
        </div>
        <div class="ms-result-body">
            <div class="ms-row">
                <span class="ms-row-key">status</span>
                <span class="ms-row-val">{status}</span>
            </div>
            <div class="ms-row">
                <span class="ms-row-key">confidence</span>
                <span class="ms-row-val">{confidence:.4f}</span>
            </div>
            {prob_rows}
            <div class="ms-bar-wrap">
                <div class="ms-bar-fill {bar_cls}" style="width:{confidence*100:.1f}%"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_upload, tab_camera = st.tabs(["Upload", "Camera"])

with tab_upload:
    uploaded = st.file_uploader(
        "drop an image or click to browse",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, use_container_width=True)
        result = call_api(img)
        if result:
            render_result(result)

with tab_camera:
    snapshot = st.camera_input("capture", label_visibility="collapsed")
    if snapshot:
        img = Image.open(snapshot).convert("RGB")
        result = call_api(img)
        if result:
            render_result(result)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="ms-footer">
    <span class="ms-dot"></span>API connected · {API_URL}
</div>
""", unsafe_allow_html=True)
