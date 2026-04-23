import os
import streamlit as st


NOMES_ESTADOS = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
    "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
    "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
    "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
}


def init_session_state():
    """Inicializa todas as variáveis de session state necessárias."""
    defaults = {
        "running_state": "idle",
        "automator": None,
        "links": [],
        "current_idx": 0,
        "manual_step": "fetching",
        "current_analysis": None,
        "current_temp_path": None,
        "modo_manual": False,
        "dialog_open": False,
        "dialog_action": None,        "template_data": None,
        "template_variables": {}    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_state():
    """Reseta o session state para o estado idle."""
    st.session_state.running_state = "idle"
    st.session_state.automator = None
    st.session_state.links = []
    st.session_state.current_idx = 0
    st.session_state.manual_step = "fetching"
    st.session_state.current_analysis = None
    if st.session_state.current_temp_path and os.path.exists(st.session_state.current_temp_path):
        try:
            os.unlink(st.session_state.current_temp_path)
        except Exception:
            pass
    st.session_state.current_temp_path = None


def safe_rerun():
    """Wrapper seguro para o st.rerun()."""
    st.rerun()
