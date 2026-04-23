import streamlit as st
import json
from pathlib import Path
from frontend.state import NOMES_ESTADOS

def load_local_templates():
    template_dir = Path("templates")
    if not template_dir.exists():
        return []
    return [f.name for f in template_dir.glob("*.json")]

def load_template_data(filename: str) -> dict:
    with open(Path("templates") / filename, "r", encoding="utf-8-sig") as f:
        return json.load(f)

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

    local_templates = load_local_templates()
    uploaded_template = st.sidebar.file_uploader("Upload de Template (.json)", type=["json"], disabled=not is_idle)
    
    template_data = None
    selected_template_name = None
    
    if uploaded_template is not None:
        try:
            content = uploaded_template.getvalue().decode("utf-8-sig")
            template_data = json.loads(content)
            selected_template_name = "Template Customizado"
            st.sidebar.success("Template carregado!")
        except Exception as e:
            st.sidebar.error("Erro ao ler JSON")
    else:
        if local_templates:
            selected_template_name = st.sidebar.selectbox(
                "Template Nativo", 
                local_templates, 
                disabled=not is_idle
            )
            if selected_template_name:
                template_data = load_template_data(selected_template_name)
        else:
            st.sidebar.warning("Nenhum template encontrado na pasta 'templates/'.")
            
    variables = {}
    if template_data:
        st.sidebar.markdown(f"**Template:** {template_data.get('nome', 'Sem nome')}")
        vars_config = template_data.get("variaveis_esperadas", [])
        
        if vars_config:
            st.sidebar.markdown('<div class="sidebar-section-label">Configuração de Variáveis</div>', unsafe_allow_html=True)
            for var in vars_config:
                var_name = var.get("nome", "")
                var_desc = var.get("descricao", var_name.capitalize())
                
                if var_name == "uf":
                    UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]
                    variables[var_name] = st.sidebar.selectbox(var_desc, UFS, disabled=not is_idle)
                    
                    if "estado" in [v.get("nome") for v in vars_config] and "estado" not in variables:
                        variables["estado"] = NOMES_ESTADOS.get(variables[var_name], "")
                elif var_name != "estado" or "estado" not in variables:
                    variables[var_name] = st.sidebar.text_input(var_desc, disabled=not is_idle)
                else:
                    st.sidebar.text_input(var_desc, value=variables["estado"], disabled=True)

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

    status_label = "🟢 Pronto" if is_idle else "🔵 Em execução"
    t_name = template_data.get("nome", "Nenhum") if template_data else "Nenhum"
    st.sidebar.markdown(f'''
    <div class="sidebar-status-card">
        <strong>{status_label}</strong><br>
        <span style="font-size:0.72rem; color: var(--text-muted);">Template: {t_name} • Limite: {limite}</span>
    </div>
    ''', unsafe_allow_html=True)

    return template_data, variables, limite, modo_manual
