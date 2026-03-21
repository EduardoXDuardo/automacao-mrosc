import streamlit as st
import streamlit.components.v1 as components
import os
import time
import base64
import shutil
from pathlib import Path
from config import logger
from automacao_mrosc import MROSCAutomator

NOMES_ESTADOS = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
}


def format_log_html(lines: list[str]) -> str:
    """Formata linhas de log para exibição HTML no terminal visual."""
    log_content = "".join(lines)
    formatted = log_content.replace("INFO", "<span class='log-info'>[INFO]</span>")\
                           .replace("ERROR", "<span class='log-error'>[ERROR]</span>")\
                           .replace("WARNING", "<span class='log-warning'>[WARNING]</span>")
    return formatted

st.set_page_config(page_title="Automação MROSC", layout="wide", page_icon="⚡")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  DESIGN SYSTEM — CSS PREMIUM COMPLETO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
        -moz-osx-font-smoothing: grayscale;
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
    @keyframes shimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes pulseGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.15); }
        50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.3); }
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
        bottom: 0;
        left: 0;
        right: 0;
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
        -webkit-backdrop-filter: blur(12px);
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
    
    /* ── Selectbox & Slider & Inputs ── */
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

    /* ── Info/Success/Warning/Error Alerts ── */
    div.stAlert {
        border-radius: var(--radius-md) !important;
        border: none !important;
        backdrop-filter: blur(8px) !important;
    }
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
        -webkit-backdrop-filter: blur(12px);
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
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 14px;
        display: inline-block;
    }
    .feature-title {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 8px;
        letter-spacing: -0.3px;
    }
    .feature-desc {
        font-size: 0.82rem;
        color: var(--text-muted);
        line-height: 1.55;
    }
    
    /* ── CTA Button ── */
    .cta-wrapper {
        text-align: center;
        margin: 36px 0 20px 0;
        animation: fadeInUp 0.6s ease-out 0.35s backwards;
    }

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
        width: 11px;
        height: 11px;
        border-radius: 50%;
        display: inline-block;
    }
    .terminal-dot.red { background: #ef4444; }
    .terminal-dot.yellow { background: #f59e0b; }
    .terminal-dot.green { background: #10b981; }
    .terminal-title-text {
        margin-left: 10px;
        font-size: 0.72rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .terminal-body {
        padding: 18px 20px;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.82rem;
        color: var(--accent-emerald);
        height: 320px;
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
    .terminal-body::-webkit-scrollbar-thumb:hover {
        background: rgba(255,255,255,0.2);
    }
    .terminal-body .log-error { color: var(--accent-rose); font-weight: 600; }
    .terminal-body .log-info { color: var(--accent-blue); }
    .terminal-body .log-warning { color: var(--accent-amber); }

    /* ── Section Header ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 28px 0 16px 0;
        animation: fadeInUp 0.4s ease-out backwards;
    }
    .section-header-icon {
        font-size: 1.3rem;
    }
    .section-header-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.4px;
    }
    .section-header-line {
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, var(--border-glass) 0%, transparent 100%);
    }

    /* ── Auto Mode Status Chip ── */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.3px;
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

    /* ── Document Viewer ── */
    .doc-viewer-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        overflow: hidden;
        backdrop-filter: blur(12px);
    }
    .doc-viewer-header {
        padding: 14px 20px;
        border-bottom: 1px solid var(--border-glass);
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── Analysis Card ── */
    .analysis-card {
        background: var(--gradient-card);
        border: 1px solid var(--border-glass);
        border-radius: var(--radius-md);
        overflow: hidden;
        backdrop-filter: blur(12px);
    }
    .analysis-header {
        padding: 14px 20px;
        border-bottom: 1px solid var(--border-glass);
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ── Relevance Badge ── */
    .badge-relevante {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 8px 18px;
        border-radius: var(--radius-sm);
        font-weight: 700;
        font-size: 0.88rem;
        letter-spacing: 0.2px;
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

    /* ── Manual Mode Step Indicator ── */
    .step-indicator {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 20px;
        animation: fadeInUp 0.4s ease-out backwards;
    }
    .step-number {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: var(--gradient-primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 0.9rem;
        color: white;
        flex-shrink: 0;
    }
    .step-text {
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .step-subtext {
        font-size: 0.8rem;
        color: var(--text-muted);
    }

    /* ── Divider ── */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border-glass) 50%, transparent 100%);
        margin: 24px 0;
    }
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent 0%, var(--border-glass) 50%, transparent 100%) !important;
        margin: 24px 0 !important;
    }

    /* ── Download Button ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent-emerald) 0%, #059669 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        padding: 0.65rem 1.4rem !important;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
        transition: all 0.25s ease !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.45) !important;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: var(--accent-indigo) !important;
    }
    
    /* ── Toast ── */
    div[data-testid="stToast"] {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }

    /* ── JSON viewer ── */
    .stJson {
        background: rgba(0, 0, 0, 0.2) !important;
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-glass) !important;
    }

    /* ── Checkbox ── */
    .stCheckbox label span {
        color: var(--text-secondary) !important;
    }

    /* ── Expander ── */
    details {
        background: var(--gradient-card) !important;
        border: 1px solid var(--border-glass) !important;
        border-radius: var(--radius-md) !important;
    }
    details summary {
        color: var(--text-primary) !important;
    }

    /* ── Markdown text ── */
    .stMarkdown p, .stMarkdown li {
        color: var(--text-secondary) !important;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: var(--text-primary) !important;
    }
    .stMarkdown strong {
        color: var(--text-primary) !important;
    }
    .stMarkdown a {
        color: var(--accent-blue) !important;
    }
</style>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━
#  SESSION STATE INIT
# ━━━━━━━━━━━━━━━━━━━━
if "running_state" not in st.session_state:
    st.session_state.running_state = "idle"
if "automator" not in st.session_state:
    st.session_state.automator = None
if "links" not in st.session_state:
    st.session_state.links = []
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0
if "manual_step" not in st.session_state:
    st.session_state.manual_step = "fetching"
if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None
if "current_temp_path" not in st.session_state:
    st.session_state.current_temp_path = None
if "modo_manual" not in st.session_state:
    st.session_state.modo_manual = False
if "dialog_open" not in st.session_state:
    st.session_state.dialog_open = False
if "dialog_action" not in st.session_state:
    st.session_state.dialog_action = None

# ━━━━━━━━━━━━━━━━
#  HERO HEADER
# ━━━━━━━━━━━━━━━━
st.markdown('''
<div class="hero-header">
    <div class="hero-icon">⚡</div>
    <div class="hero-title">Automação MROSC</div>
    <div class="hero-subtitle">Inteligência Artificial direcionada à análise de documentos e parcerias públicas do Marco Regulatório das OSCs</div>
    <div class="hero-badge">Powered by Gemini AI</div>
</div>
''', unsafe_allow_html=True)

# ━━━━━━━━━━━━━━
#  SIDEBAR
# ━━━━━━━━━━━━━━
st.sidebar.markdown('''
<div class="sidebar-header">
    <div class="sidebar-title">⚙️ Painel de Controle</div>
    <div class="sidebar-desc">Configure os parâmetros da automação</div>
</div>
''', unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-section-label">Localização</div>', unsafe_allow_html=True)
estado = st.sidebar.selectbox("Estado alvo (UF)", [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
], disabled=(st.session_state.running_state != "idle"))

st.sidebar.markdown('<div class="sidebar-section-label">Parâmetros</div>', unsafe_allow_html=True)
limite = st.sidebar.slider("Limite de resultados por query", 1, 50, 10, disabled=(st.session_state.running_state != "idle"))

st.sidebar.markdown('<div class="sidebar-section-label">Modo de Execução</div>', unsafe_allow_html=True)
modo_manual = st.sidebar.checkbox("Modo Manual (Aprovação Passo a Passo)", value=False, disabled=(st.session_state.running_state != "idle"))

# Sidebar status card
status_label = "🟢 Pronto" if st.session_state.running_state == "idle" else "🔵 Em execução"
st.sidebar.markdown(f'''
<div class="sidebar-status-card">
    <strong>{status_label}</strong><br>
    <span style="font-size:0.72rem; color: var(--text-muted);">Estado: {NOMES_ESTADOS.get(estado, estado)} • Limite: {limite}</span>
</div>
''', unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━
#  HELPER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━
def safe_rerun():
    st.rerun()

def process_manual_action(action, url, path, analysis, automator):
    if action == "approve":
        automator.process_and_save_document(url, Path(path), analysis)
        st.toast("✅ Documento aprovado e salvo com sucesso!")
    elif action == "skip":
        st.toast("⏭️ Documento descartado.")
        
    if path and os.path.exists(path):
        try: os.unlink(path)
        except Exception: pass
        
    st.session_state.current_idx += 1
    st.session_state.manual_step = "next"
    safe_rerun()

def render_terminal(lines: list[str], title: str = "Automação MROSC"):
    """Renderiza terminal estilizado com header macOS-style."""
    formatted = format_log_html(lines)
    return f'''
    <div class="terminal-container">
        <div class="terminal-header">
            <span class="terminal-dot red"></span>
            <span class="terminal-dot yellow"></span>
            <span class="terminal-dot green"></span>
            <span class="terminal-title-text">{title}</span>
        </div>
        <div class="terminal-body">{formatted}</div>
    </div>
    '''

def render_section_header(icon: str, title: str):
    """Renderiza um header de seção estilizado."""
    st.markdown(f'''
    <div class="section-header">
        <span class="section-header-icon">{icon}</span>
        <span class="section-header-title">{title}</span>
        <div class="section-header-line"></div>
    </div>
    ''', unsafe_allow_html=True)

def render_document_review(url, path, analysis, automator, idx, total):
    # Step Indicator
    st.markdown(f'''
    <div class="step-indicator">
        <div class="step-number">{idx + 1}</div>
        <div>
            <div class="step-text">Analisando Documento {idx + 1} de {total}</div>
            <div class="step-subtext">Aguardando sua decisão</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown(f"**Fonte:** [{url}]({url})")
    
    act1, act2 = st.columns(2)
    with act1:
        if st.button("✅  Aprovar & Salvar", use_container_width=True, type="primary", key=f"btn_approve_{idx}"):
            process_manual_action("approve", url, path, analysis, automator)
    with act2:
        if st.button("⏭️  Pular / Descartar", use_container_width=True, type="secondary", key=f"btn_skip_{idx}"):
            process_manual_action("skip", url, path, analysis, automator)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    c_doc, c_ia = st.columns([1.4, 1])
    with c_doc:
        st.markdown('''
        <div class="doc-viewer-header">
            <span>📄</span> Visualização do Documento
        </div>
        ''', unsafe_allow_html=True)
        try:
            if path.endswith(".html"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    components.html(f"<div style='height:600px; padding:15px; overflow-y:auto; background:#fff; color:#1e293b; font-family:Inter,sans-serif; font-size:14px;'>{content}</div>", height=600, scrolling=True)
            elif path.endswith(".pdf"):
                with open(path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf" style="border:none; border-radius:8px;"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.info(f"Arquivo `{path}` baixado com sucesso. Formato não renderizável diretamente.")
        except Exception as e:
            st.error(f"Erro ao carregar visualização: {e}")

    with c_ia:
        st.markdown('''
        <div class="analysis-header">
            <span>🤖</span> Análise da Inteligência Artificial
        </div>
        ''', unsafe_allow_html=True)
        
        with st.container(height=600):
            if isinstance(analysis, dict):
                is_relevant = analysis.get("relevante")
                if is_relevant:
                    st.markdown('<div class="badge-relevante yes">✅ Recomendação: RELEVANTE</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-relevante no">❌ Recomendação: NÃO RELEVANTE</div>', unsafe_allow_html=True)
                
                st.markdown("")  # spacer
                st.json(analysis, expanded=True)
            else:
                st.error("Falha na análise ou não obteve JSON válido da IA.")

def reset_state():
    st.session_state.running_state = "idle"
    st.session_state.automator = None
    st.session_state.links = []
    st.session_state.current_idx = 0
    st.session_state.manual_step = "fetching"
    st.session_state.current_analysis = None
    if st.session_state.current_temp_path and os.path.exists(st.session_state.current_temp_path):
        try: os.unlink(st.session_state.current_temp_path)
        except Exception: pass
    st.session_state.current_temp_path = None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  IDLE STATE — WELCOME PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if st.session_state.running_state == "idle":
    st.markdown('''
    <div class="welcome-info">
        <strong>Bem-vindo ao Automação MROSC.</strong> Este sistema utiliza Inteligência Artificial para buscar, baixar e classificar automaticamente editais, parcerias, pautas, relatórios e manuais do MROSC nos portais oficiais dos estados brasileiros. Configure os parâmetros na barra lateral e inicie a automação.
    </div>
    ''', unsafe_allow_html=True)

    st.markdown('''
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Busca Inteligente</div>
            <div class="feature-desc">Varredura automática em portais oficiais utilizando queries especializadas em MROSC e parcerias com OSCs.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">Análise com Gemini AI</div>
            <div class="feature-desc">Cada documento é analisado pela IA que classifica relevância, tipo, dimensão e extrai metadados estruturados.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Relatórios Consolidados</div>
            <div class="feature-desc">Resultados exportados em planilha Excel com todos os metadados e documentos originais arquivados.</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("")  # spacer

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("🚀  Iniciar Automação", use_container_width=True, type="primary"):
            os.makedirs("logs", exist_ok=True)
            if not os.path.exists("logs/automacao.log"):
                open("logs/automacao.log", "w", encoding="utf-8").close()
                
            st.session_state.modo_manual = modo_manual
            st.session_state.running_state = "running_manual" if modo_manual else "running_auto"
            safe_rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  EXECUTION STATE — AUTO & MANUAL MODES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if st.session_state.running_state != "idle":
    col_title, col_stop = st.columns([4, 1])
    with col_stop:
        if st.button("🛑  Parar", use_container_width=True, type="secondary"):
            reset_state()
            safe_rerun()

    nome_estado = NOMES_ESTADOS.get(estado, estado)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ── MODO AUTOMÁTICO ──
    if st.session_state.running_state == "running_auto":
        render_section_header("⚡", "Execução Automática em Andamento")
        
        st.markdown('<span class="status-chip running">● Processando</span>', unsafe_allow_html=True)
        st.markdown("")
        
        m1, m2, m3 = st.columns(3)
        metric_total = m1.empty()
        metric_current = m2.empty()
        metric_saved = m3.empty()
        
        metric_total.metric("🔗 Links Encontrados", "0")
        metric_current.metric("⏳ Processando Agora", "0 / 0")
        metric_saved.metric("💾 Documentos Salvos", "0")
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        progress_bar = st.progress(0)
        status_text = st.empty()
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('''
            <div class="doc-viewer-header">
                <span>📄</span> Último Arquivo Processado
            </div>
            ''', unsafe_allow_html=True)
            viewer_placeholder = st.empty()
        with col2:
            st.markdown('''
            <div class="analysis-header">
                <span>🤖</span> Última Análise da IA
            </div>
            ''', unsafe_allow_html=True)
            ai_placeholder = st.empty()

        if not st.session_state.automator:
            st.session_state.automator = MROSCAutomator(uf=estado, estado=nome_estado, limit=limite)
            
        def automator_callback(event):
            try:
                if event["type"] == "status":
                    status_text.info(f"**Status:** {event['message']}")
                elif event["type"] == "links_found":
                    metric_total.metric("🔗 Links Encontrados", event['total'])
                    status_text.success(f"Busca finalizada. **{event['total']}** links encontrados na web.")
                elif event["type"] == "downloading":
                    pct = event["current"] / event["total"]
                    progress_bar.progress(pct)
                    metric_current.metric("⏳ Processando Agora", f"{event['current']} / {event['total']}")
                    status_text.warning(f"**Baixando:** {event['url']}")
                    ai_placeholder.info("Aguardando processamento da IA...")
                    viewer_placeholder.info("Baixando arquivo...")
                elif event["type"] == "downloaded":
                    path = event["path"]
                    try:
                        viewer_placeholder.empty()
                        if path.endswith(".html"):
                            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                                content = f.read()
                                with viewer_placeholder.container():
                                    components.html(f"<div style='height:500px; padding:15px; overflow-y:auto; background:#fff; color:#1e293b; font-family:Inter,sans-serif; font-size:13px; border-radius:8px;'>{content}</div>", height=520, scrolling=False)
                        elif path.endswith(".pdf"):
                            with open(path, "rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="520" type="application/pdf" style="border:none; border-radius:8px;"></iframe>'
                            viewer_placeholder.markdown(pdf_display, unsafe_allow_html=True)
                        else:
                            viewer_placeholder.info(f"Arquivo recebido: {path}")
                    except Exception as e:
                        viewer_placeholder.error(f"Não foi possível visualizar: {e}")
                elif event["type"] == "analysis_done":
                    analysis = event.get("analysis")
                    ai_placeholder.empty()
                    with ai_placeholder.container():
                        if isinstance(analysis, dict):
                            if analysis.get("relevante"):
                                st.success(f"**Relevante:** {analysis.get('titulo', 'Documento sem título')}")
                            else:
                                st.error("**Não Relevante:** Arquivo descartado.")
                            st.json(analysis, expanded=True)
                        else:
                            st.warning("Falha na análise ou retorno inesperado.")
                elif event["type"] == "saved":
                    saved_count = len(st.session_state.automator.output_manager.results)
                    metric_saved.metric("💾 Documentos Salvos", f"{saved_count}")
                elif event["type"] == "done":
                    progress_bar.progress(1.0)
                    status_text.success(f"**Finalizado!** {event['results_count']} documentos relevantes salvos com sucesso.")
                
                if 'log_placeholder' in st.session_state and os.path.exists("logs/automacao.log"):
                    with open("logs/automacao.log", "r", encoding="utf-8") as f:
                        lines = f.readlines()[-30:]
                        st.session_state.log_placeholder.markdown(
                            render_terminal(lines, "Log de Execução"), 
                            unsafe_allow_html=True
                        )

            except Exception as callback_err:
                logger.debug(f"[UI_CALLBACK] Erro no callback do Streamlit (não-fatal): {callback_err}")
        
        render_section_header("📋", "Diário de Execução em Tempo Real")
        st.session_state.log_placeholder = st.empty()
        
        if os.path.exists("logs/automacao.log"):
            with open("logs/automacao.log", "r", encoding="utf-8") as f:
                lines = f.readlines()[-30:]
                st.session_state.log_placeholder.markdown(render_terminal(lines, "Log de Execução"), unsafe_allow_html=True)

        st.session_state.automator.run(ui_callback=automator_callback)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown('<span class="status-chip done">● Concluído</span>', unsafe_allow_html=True)
        st.success("Automação em Lote concluída com sucesso!")
        
        base_dir = st.session_state.automator.output_manager.base_dir
        if base_dir and os.path.exists(base_dir):
            zip_path = str(base_dir) + ".zip"
            if not os.path.exists(zip_path):
                shutil.make_archive(str(base_dir), 'zip', str(base_dir))
            
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="📦  Baixar Resultados (.zip)",
                    data=f,
                    file_name=os.path.basename(zip_path),
                    mime="application/zip"
                )

        if st.button("🏁  Finalizar e Voltar", key="btn_finalizar", type="primary"):
            reset_state()
            safe_rerun()

    # ── MODO MANUAL ──
    elif st.session_state.running_state == "running_manual":
        if not st.session_state.automator:
            st.session_state.automator = MROSCAutomator(uf=estado, estado=nome_estado, limit=limite)
            with st.spinner("Realizando buscas na internet... (Aguarde)"):
                st.session_state.links = st.session_state.automator.searcher.collect_links()
            st.session_state.manual_step = "next"
            safe_rerun()

        automator = st.session_state.automator
        links = st.session_state.links
        idx = st.session_state.current_idx
        total = len(links)

        if idx >= total:
            st.markdown('<span class="status-chip done">● Concluído</span>', unsafe_allow_html=True)
            st.success(f"Fim da lista! **{total}** documentos processados.")
            automator.output_manager.save_excel(incremental=False)            
            base_dir = automator.output_manager.base_dir
            if base_dir and os.path.exists(base_dir):
                zip_path = str(base_dir) + ".zip"
                if not os.path.exists(zip_path):
                    shutil.make_archive(str(base_dir), 'zip', str(base_dir))
                
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="📦  Baixar Resultados (.zip)",
                        data=f,
                        file_name=os.path.basename(zip_path),
                        mime="application/zip"
                    )
            if st.button("🏁  Concluir Processo", type="primary"):
                reset_state()
                safe_rerun()
            st.stop()

        render_section_header("🔬", "Modo Manual — Revisão de Documentos")
        
        st.progress((idx) / total if total > 0 else 0)
        st.markdown(f'<span class="status-chip running">● Link {idx + 1} de {total}</span>', unsafe_allow_html=True)
        st.markdown("")
        
        url = links[idx]
        
        if st.session_state.manual_step == "next":
            st.session_state.manual_step = "analyzing"
            safe_rerun()

        if st.session_state.manual_step == "analyzing":
            with st.spinner("Baixando documento e processando com IA..."):
                temp_path = automator.downloader.download(url)
                if not temp_path:
                    st.error("Falha ao baixar o arquivo.")
                    time.sleep(1)
                    st.session_state.current_idx += 1
                    st.session_state.manual_step = "next"
                    safe_rerun()
                
                st.session_state.current_temp_path = str(temp_path)
                
                parts = automator.processor.get_document_content(temp_path)
                if not parts:
                    st.warning("Falha na extração de texto (arquivo vazio ou inválido).")
                    time.sleep(1)
                    try: temp_path.unlink()
                    except Exception: pass
                    st.session_state.current_idx += 1
                    st.session_state.manual_step = "next"
                    safe_rerun()
                
                analysis = automator.processor.analyze(parts, url, automator.estado)
                st.session_state.current_analysis = analysis
                st.session_state.manual_step = "waiting"
                safe_rerun()

        if st.session_state.manual_step == "waiting":
            render_document_review(
                url, 
                st.session_state.current_temp_path, 
                st.session_state.current_analysis, 
                automator, 
                idx, 
                total
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LOG VIEWER — IDLE STATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if st.session_state.running_state == "idle":
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    render_section_header("📋", "Histórico de Execução")
    
    if os.path.exists("logs/automacao.log"):
        with open("logs/automacao.log", "r", encoding="utf-8") as f:
            lines = f.readlines()[-30:]
            if lines:
                st.markdown(render_terminal(lines, "automacao.log"), unsafe_allow_html=True)
            else:
                st.info("Log vazio. Inicie uma automação para gerar registros.")
        
        st.markdown("")
        if st.button("🗑️  Limpar Histórico de Logs", type="secondary"):
            open("logs/automacao.log", "w").close()
            st.rerun()
    else:
        st.info("Nenhum log gerado ainda. Inicie uma automação para começar.")
