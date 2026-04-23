import streamlit as st
from frontend.styles import inject_css
from frontend.state import init_session_state
from frontend.components import render_hero_header
from frontend.sidebar import render_sidebar
from frontend.welcome import render_welcome
from frontend.auto_mode import render_auto_mode
from frontend.manual_mode import render_manual_mode
from frontend.template_editor import render_template_editor

# ── Configuração da Página ──
st.set_page_config(page_title="Automação MROSC", layout="wide", page_icon="⚡")

# ── Design System ──
inject_css()

# ── Session State ──
init_session_state()

# ── Header ──
render_hero_header()

# ── Sidebar ──
template_data, variables, limite, modo_manual = render_sidebar()

# ── Roteamento de Páginas ──
if st.session_state.running_state == "idle":
    render_welcome(modo_manual, template_data)
elif st.session_state.running_state == "running_auto":
    render_auto_mode(template_data, variables, limite)
elif st.session_state.running_state == "running_manual":
    render_manual_mode(template_data, variables, limite)
elif st.session_state.running_state == "template_editor":
    render_template_editor()
