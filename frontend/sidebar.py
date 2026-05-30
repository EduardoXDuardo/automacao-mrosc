import json
from html import escape
from pathlib import Path

import streamlit as st

from frontend.state import NOMES_ESTADOS


UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]


def load_local_templates():
    template_dir = Path("templates")
    if not template_dir.exists():
        return []
    return sorted(f.name for f in template_dir.glob("*.json"))


def load_template_data(filename: str) -> dict:
    with open(Path("templates") / filename, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _find_var_config(vars_config: list[dict], name: str) -> dict | None:
    return next((var for var in vars_config if var.get("nome") == name), None)


def _render_template_picker(is_idle: bool) -> tuple[dict | None, str | None]:
    local_templates = load_local_templates()

    uploaded_template = st.sidebar.file_uploader(
        "Upload de Template (.json)",
        type=["json"],
        key="sidebar_uploaded_template",
        disabled=not is_idle,
    )

    if uploaded_template is not None:
        try:
            content = uploaded_template.getvalue().decode("utf-8-sig")
            template_data = json.loads(content)
            if not isinstance(template_data, dict):
                raise ValueError("O arquivo precisa conter um objeto JSON.")
            st.sidebar.success("Template carregado!")
            return template_data, "Template customizado"
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as err:
            st.sidebar.error(f"Erro ao ler JSON: {err}")
            return None, None

    if not local_templates:
        st.sidebar.warning("Nenhum template encontrado na pasta 'templates/'.")
        return None, None

    selected_template_name = st.sidebar.selectbox(
        "Template Nativo",
        local_templates,
        key="sidebar_template_name",
        disabled=not is_idle,
    )

    if not selected_template_name:
        return None, None

    try:
        return load_template_data(selected_template_name), selected_template_name
    except (OSError, json.JSONDecodeError) as err:
        st.sidebar.error(f"Erro ao carregar template: {err}")
        return None, selected_template_name


def _render_template_variables(template_data: dict, is_idle: bool) -> dict:
    variables = {}
    vars_config = template_data.get("variaveis_esperadas", [])

    if not vars_config:
        return variables

    st.sidebar.markdown(
        '<div class="sidebar-section-label">Configuração de Variáveis</div>',
        unsafe_allow_html=True,
    )

    uf_config = _find_var_config(vars_config, "uf")
    estado_config = _find_var_config(vars_config, "estado")

    if uf_config:
        current_uf = st.session_state.get("sidebar_var_uf", "BA")
        if current_uf not in UFS:
            current_uf = "BA"

        variables["uf"] = st.sidebar.selectbox(
            uf_config.get("descricao", "UF"),
            UFS,
            index=UFS.index(current_uf),
            key="sidebar_var_uf",
            disabled=not is_idle,
        )

        if estado_config:
            variables["estado"] = NOMES_ESTADOS.get(variables["uf"], "")
            st.sidebar.text_input(
                estado_config.get("descricao", "Estado"),
                value=variables["estado"],
                disabled=True,
            )

    for var in vars_config:
        var_name = var.get("nome", "").strip()
        if not var_name:
            continue

        if var_name == "uf" or (var_name == "estado" and uf_config):
            continue

        var_desc = var.get("descricao", var_name.capitalize())
        variables[var_name] = st.sidebar.text_input(
            var_desc,
            key=f"sidebar_var_{var_name}",
            disabled=not is_idle,
        )

    return variables


def render_sidebar() -> tuple[dict, dict, int, bool]:
    """Renderiza a sidebar completa e retorna (template_data, variables, limite, modo_manual)."""

    st.sidebar.markdown('''
    <div class="sidebar-header">
        <div class="sidebar-title">⚙️ Painel de Controle</div>
        <div class="sidebar-desc">Configure os parâmetros da automação</div>
    </div>
    ''', unsafe_allow_html=True)

    is_idle = st.session_state.running_state == "idle"

    st.sidebar.markdown('<div class="sidebar-section-label">Template de Busca</div>', unsafe_allow_html=True)

    if st.sidebar.button("📝 Criar Novo / Editar", use_container_width=True, disabled=not is_idle):
        st.session_state.running_state = "template_editor"
        st.rerun()

    template_data, selected_template_name = _render_template_picker(is_idle)
    variables = {}

    if template_data:
        template_name = escape(str(template_data.get("nome") or selected_template_name or "Sem nome"))
        template_desc = template_data.get("descricao")
        st.sidebar.markdown(f'<div class="sidebar-template-name">{template_name}</div>', unsafe_allow_html=True)
        if template_desc:
            st.sidebar.caption(str(template_desc))
        variables = _render_template_variables(template_data, is_idle)

    st.sidebar.markdown('<div class="sidebar-section-label">Parâmetros</div>', unsafe_allow_html=True)
    limite = st.sidebar.slider(
        "Limite de resultados por query",
        1,
        50,
        st.session_state.get("limite", 10),
        key="sidebar_limite",
        disabled=not is_idle,
    )

    st.sidebar.markdown('<div class="sidebar-section-label">Modo de Execução</div>', unsafe_allow_html=True)
    modo_manual = st.sidebar.checkbox(
        "Modo Manual (Aprovação Passo a Passo)",
        value=st.session_state.get("modo_manual", False),
        key="sidebar_modo_manual",
        disabled=not is_idle,
    )

    if is_idle:
        st.session_state.template_data = template_data
        st.session_state.template_variables = variables
        st.session_state.limite = limite
        st.session_state.modo_manual = modo_manual
    else:
        template_data = st.session_state.get("template_data") or template_data
        variables = st.session_state.get("template_variables") or variables
        limite = st.session_state.get("limite", limite)
        modo_manual = st.session_state.get("modo_manual", modo_manual)

    status_label = "🟢 Pronto" if is_idle else "🔵 Em execução"
    t_name = escape(str(template_data.get("nome") or "Nenhum")) if template_data else "Nenhum"
    st.sidebar.markdown(f'''
    <div class="sidebar-status-card">
        <strong>{status_label}</strong><br>
        <span style="font-size:0.72rem; color: var(--text-muted);">Template: {t_name} • Limite: {limite}</span>
    </div>
    ''', unsafe_allow_html=True)

    return template_data, variables, limite, modo_manual
