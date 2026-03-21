import streamlit as st
from frontend.state import NOMES_ESTADOS


def render_sidebar() -> tuple[str, int, bool]:
    """Renderiza a sidebar completa e retorna (estado, limite, modo_manual)."""
    
    st.sidebar.markdown('''
    <div class="sidebar-header">
        <div class="sidebar-title">⚙️ Painel de Controle</div>
        <div class="sidebar-desc">Configure os parâmetros da automação</div>
    </div>
    ''', unsafe_allow_html=True)

    is_idle = st.session_state.running_state == "idle"

    st.sidebar.markdown('<div class="sidebar-section-label">Localização</div>', unsafe_allow_html=True)
    estado = st.sidebar.selectbox("Estado alvo (UF)", [
        "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
        "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
        "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
    ], disabled=(not is_idle))

    st.sidebar.markdown('<div class="sidebar-section-label">Parâmetros</div>', unsafe_allow_html=True)
    limite = st.sidebar.slider(
        "Limite de resultados por query", 1, 50, 10,
        disabled=(not is_idle)
    )

    st.sidebar.markdown('<div class="sidebar-section-label">Modo de Execução</div>', unsafe_allow_html=True)
    modo_manual = st.sidebar.checkbox(
        "Modo Manual (Aprovação Passo a Passo)",
        value=False,
        disabled=(not is_idle)
    )

    # Status card
    status_label = "🟢 Pronto" if is_idle else "🔵 Em execução"
    nome_estado = NOMES_ESTADOS.get(estado, estado)
    st.sidebar.markdown(f'''
    <div class="sidebar-status-card">
        <strong>{status_label}</strong><br>
        <span style="font-size:0.72rem; color: var(--text-muted);">Estado: {nome_estado} • Limite: {limite}</span>
    </div>
    ''', unsafe_allow_html=True)

    return estado, limite, modo_manual
