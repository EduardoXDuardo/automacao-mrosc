import streamlit as st


def inject_css():
    """Injeta o design system CSS premium completo."""
    st.markdown("""
<style>
    /* ── Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');
    
    :root {
        --bg-primary: #0a0f1e;
        --bg-secondary: #111827;
        --bg-card: rgba(17, 24, 39, 0.7);
        --bg-glass: rgba(255, 255, 255, 0.03);
        --border-glass: rgba(255, 255, 255, 0.08);
        --border-subtle: rgba(255, 255, 255, 0.06);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-blue: #3b82f6;
        --accent-indigo: #6366f1;
        --accent-purple: #8b5cf6;
        --accent-cyan: #06b6d4;
        --accent-emerald: #10b981;
        --accent-amber: #f59e0b;
        --accent-rose: #f43f5e;
        --gradient-primary: linear-gradient(135deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
        --gradient-header: linear-gradient(135deg, #0f172a 0%, #1e1b4b 40%, #0f172a 100%);
        --gradient-card: linear-gradient(145deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
        --shadow-lg: 0 20px 60px -15px rgba(0, 0, 0, 0.5);
        --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.3);
        --shadow-glow-blue: 0 0 30px rgba(59, 130, 246, 0.15);
        --radius-lg: 16px;
        --radius-md: 12px;
        --radius-sm: 8px;
    }
    
    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }
    
    .stApp {
        background: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }
    .stApp > header { background: transparent !important; }
    .stMainBlockContainer {
        padding-top: 1rem !important;
        max-width: 1280px !important;
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden !important; }

    /* ── Keyframe Animations ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-6px); }
    }
    @keyframes progressPulse {
        0% { opacity: 0.8; }
        50% { opacity: 1; }
        100% { opacity: 0.8; }
    }

    /* ── Header ── */
    .hero-header {
        position: relative;
        padding: 52px 32px 44px 32px;
        text-align: center;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 35%, #312e81 60%, #1e1b4b 85%, #0f172a 100%);
        background-size: 300% 300%;
        animation: gradientShift 8s ease infinite;
        border-radius: var(--radius-lg);
        margin-bottom: 36px;
        border: 1px solid var(--border-glass);
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        inset: 0;
        background: radial-gradient(circle at 30% 40%, rgba(99, 102, 241, 0.12) 0%, transparent 60%),
                    radial-gradient(circle at 70% 60%, rgba(139, 92, 246, 0.08) 0%, transparent 50%);
        pointer-events: none;
    }
    .hero-header::after {
        content: '';
        position: absolute;
        bottom: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, rgba(99,102,241,0.4) 50%, transparent 100%);
    }
    .hero-icon {
        font-size: 2.8rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
        margin-bottom: 8px;
        filter: drop-shadow(0 0 12px rgba(99, 102, 241, 0.4));
    }
    .hero-title {
        font-weight: 900;
        font-size: 2.8rem;
        letter-spacing: -1.5px;
        background: linear-gradient(135deg, #f1f5f9 0%, #c7d2fe 50%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 4px 0 0 0;
        line-height: 1.1;
    }
    .hero-subtitle {
        color: var(--text-secondary);
        font-size: 1.05rem;
        font-weight: 400;
        margin-top: 12px;
        letter-spacing: 0.2px;
        max-width: 550px;
        margin-left: auto;
        margin-right: auto;
    }
    .hero-badge {
        display: inline-block;
        margin-top: 18px;
        padding: 5px 16px;
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        color: #a5b4fc;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%) !important;
        border-right: 1px solid var(--border-glass) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown h4 {
        color: var(--text-primary) !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label,
    section[data-testid="stSidebar"] .stCheckbox label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }
    .sidebar-header {
        padding: 16px 0 18px 0;
        border-bottom: 1px solid var(--border-glass);
        margin-bottom: 20px;
    }
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.3px;
    }
    .sidebar-desc {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 4px;
    }
    .sidebar-section-label {
        display: block;
        font-size: 0.68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: var(--text-muted);
        margin: 24px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 1px solid var(--border-subtle);
    }
    .sidebar-status-card {
        margin-top: 24px;
        padding: 14px 16px;
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: var(--radius-sm);
        font-size: 0.8rem;
        color: var(--accent-emerald);
    }

    /* ── Buttons ── */
    .stButton > button {
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.65rem 1.4rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: -0.1px !important;
        font-size: 0.9rem !important;
    }
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.45) !important;
    }
    .stButton > button[kind="secondary"],
    .stButton > button[data-testid="stBaseButton-secondary"] {
        background: rgba(255, 255, 255, 0.05) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-glass) !important;
    }
    .stButton > button[kind="secondary"]:hover,
    .stButton > button[data-testid="stBaseButton-secondary"]:hover {
        background: rgba(255, 255, 255, 0.1) !important;
        transform: translateY(-2px) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
    }

    /* ── Metrics ── */
    div.stMetric {
        background: var(--gradient-card);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 22px 24px;
        backdrop-filter: blur(12px);
        box-shadow: var(--shadow-card);
        animation: fadeInUp 0.5s ease-out backwards;
    }
    div[data-testid="stMetricValue"] {
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        font-size: 2rem !important;
    }
    div[data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Progress Bar ── */
    div.stProgress > div > div > div {
        background: var(--gradient-primary) !important;
        border-radius: 6px !important;
        animation: progressPulse 2s ease-in-out infinite;
    }
    div.stProgress > div > div {
        background: rgba(255, 255, 255, 0.06) !important;
        border-radius: 6px !important;
    }
    
    /* ── Selectbox & Slider ── */
    div[data-baseweb="select"] > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }
    div[data-baseweb="select"] > div:hover {
        border-color: rgba(99, 102, 241, 0.4) !important;
    }
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background: var(--accent-indigo) !important;
    }

    /* ── Alerts ── */
    div.stAlert { border-radius: var(--radius-md) !important; border: none !important; }
    div[data-testid="stAlertContentInfo"] {
        background: rgba(59, 130, 246, 0.08) !important;
        border-left: 4px solid var(--accent-blue) !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stAlertContentSuccess"] {
        background: rgba(16, 185, 129, 0.08) !important;
        border-left: 4px solid var(--accent-emerald) !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stAlertContentWarning"] {
        background: rgba(245, 158, 11, 0.08) !important;
        border-left: 4px solid var(--accent-amber) !important;
        color: var(--text-primary) !important;
    }
    div[data-testid="stAlertContentError"] {
        background: rgba(244, 63, 94, 0.08) !important;
        border-left: 4px solid var(--accent-rose) !important;
        color: var(--text-primary) !important;
    }

    /* ── Feature Cards ── */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 28px 0;
    }
    .feature-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        padding: 28px 24px;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.5s ease-out backwards;
    }
    .feature-card:nth-child(1) { animation-delay: 0.05s; }
    .feature-card:nth-child(2) { animation-delay: 0.15s; }
    .feature-card:nth-child(3) { animation-delay: 0.25s; }
    .feature-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.25);
        box-shadow: var(--shadow-glow-blue);
    }
    .feature-icon { font-size: 2rem; margin-bottom: 14px; display: inline-block; }
    .feature-title {
        font-size: 1rem; font-weight: 700; color: var(--text-primary);
        margin-bottom: 8px; letter-spacing: -0.3px;
    }
    .feature-desc { font-size: 0.82rem; color: var(--text-muted); line-height: 1.55; }

    /* ── Welcome Info Box ── */
    .welcome-info {
        background: rgba(59, 130, 246, 0.06);
        border: 1px solid rgba(59, 130, 246, 0.12);
        border-left: 4px solid var(--accent-blue);
        border-radius: var(--radius-sm);
        padding: 18px 22px;
        color: var(--text-secondary);
        font-size: 0.88rem;
        line-height: 1.65;
        animation: fadeInUp 0.5s ease-out 0.1s backwards;
    }

    /* ── Terminal Log ── */
    .terminal-container {
        background: #0c1222;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-glass);
        overflow: hidden;
        box-shadow: var(--shadow-card);
        animation: fadeInUp 0.5s ease-out backwards;
    }
    .terminal-header {
        background: rgba(255, 255, 255, 0.04);
        padding: 10px 16px;
        display: flex;
        align-items: center;
        gap: 8px;
        border-bottom: 1px solid var(--border-glass);
    }
    .terminal-dot {
        width: 11px; height: 11px; border-radius: 50%; display: inline-block;
    }
    .terminal-dot.red { background: #ef4444; }
    .terminal-dot.yellow { background: #f59e0b; }
    .terminal-dot.green { background: #10b981; }
    .terminal-title-text {
        margin-left: 10px;
        font-size: 0.72rem; font-weight: 600; color: var(--text-muted);
        text-transform: uppercase; letter-spacing: 1px;
    }
    .terminal-body {
        padding: 18px 20px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.78rem;
        color: var(--accent-emerald);
        max-height: 500px;
        overflow-y: auto;
        white-space: pre-wrap;
        line-height: 1.7;
    }
    .terminal-body::-webkit-scrollbar { width: 6px; }
    .terminal-body::-webkit-scrollbar-track { background: transparent; }
    .terminal-body::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.1);
        border-radius: 3px;
    }
    .terminal-body::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }
    .terminal-body .log-error { color: var(--accent-rose); font-weight: 600; }
    .terminal-body .log-info { color: var(--accent-blue); }
    .terminal-body .log-warning { color: var(--accent-amber); }

    /* ── Section Header ── */
    .section-header {
        display: flex; align-items: center; gap: 10px;
        margin: 28px 0 16px 0;
        animation: fadeInUp 0.4s ease-out backwards;
    }
    .section-header-icon { font-size: 1.3rem; }
    .section-header-title {
        font-size: 1.15rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.4px;
    }
    .section-header-line {
        flex: 1; height: 1px;
        background: linear-gradient(90deg, var(--border-glass) 0%, transparent 100%);
    }

    /* ── Status Chip ── */
    .status-chip {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 14px; border-radius: 20px;
        font-size: 0.78rem; font-weight: 600; letter-spacing: 0.3px;
    }
    .status-chip.running {
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.25);
        color: #a5b4fc;
    }
    .status-chip.done {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: var(--accent-emerald);
    }

    /* ── Document Viewer & Analysis Headers ── */
    .panel-header {
        padding: 14px 20px;
        border-bottom: 1px solid var(--border-glass);
        font-weight: 600; font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase; letter-spacing: 0.5px;
        display: flex; align-items: center; gap: 8px;
        background: var(--gradient-card);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md) var(--radius-md) 0 0;
    }

    /* ── Relevance Badge ── */
    .badge-relevante {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 8px 18px; border-radius: var(--radius-sm);
        font-weight: 700; font-size: 0.88rem; letter-spacing: 0.2px;
    }
    .badge-relevante.yes {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.25);
        color: var(--accent-emerald);
    }
    .badge-relevante.no {
        background: rgba(244, 63, 94, 0.12);
        border: 1px solid rgba(244, 63, 94, 0.25);
        color: var(--accent-rose);
    }

    /* ── Step Indicator ── */
    .step-indicator {
        display: flex; align-items: center; gap: 12px; margin-bottom: 20px;
        animation: fadeInUp 0.4s ease-out backwards;
    }
    .step-number {
        width: 36px; height: 36px; border-radius: 50%;
        background: var(--gradient-primary);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 0.9rem; color: white; flex-shrink: 0;
    }
    .step-text { font-size: 1rem; font-weight: 600; color: var(--text-primary); }
    .step-subtext { font-size: 0.8rem; color: var(--text-muted); }

    /* ── Divider ── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border-glass) 50%, transparent 100%);
        margin: 24px 0;
    }
    hr {
        border: none !important; height: 1px !important;
        background: linear-gradient(90deg, transparent 0%, var(--border-glass) 50%, transparent 100%) !important;
        margin: 24px 0 !important;
    }

    /* ── Download Button ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent-emerald) 0%, #059669 100%) !important;
        color: white !important; border: none !important;
        border-radius: var(--radius-sm) !important; font-weight: 600 !important;
        padding: 0.65rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.45) !important;
    }

    /* ── Misc ── */
    div[data-testid="stToast"] {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }
    .stJson {
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-glass) !important;
    }
    .stCheckbox label span { color: var(--text-secondary) !important; }
    details {
        background: var(--gradient-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
    }
    details summary { color: var(--text-primary) !important; }
    .stMarkdown p, .stMarkdown li { color: var(--text-secondary) !important; }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 { color: var(--text-primary) !important; }
    .stMarkdown strong { color: var(--text-primary) !important; }
    .stMarkdown a { color: var(--accent-blue) !important; }
</style>
""", unsafe_allow_html=True)
