import streamlit as st
import os
import time
import base64
from pathlib import Path
from config import logger 

st.set_page_config(page_title="Automação MROSC", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #1F618D;
        font-family: 'Arial', sans-serif;
        font-weight: 700;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #7F8C8D;
        font-size: 1.1em;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    div[data-testid="stSidebar"] {
        background-color: #f8f9f9;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

if "running_state" not in st.session_state:
    st.session_state.running_state = "idle" # idle, running_auto, running_manual
if "automator" not in st.session_state:
    st.session_state.automator = None
if "links" not in st.session_state:
    st.session_state.links = []
if "current_idx" not in st.session_state:
    st.session_state.current_idx = 0
if "manual_step" not in st.session_state:
    st.session_state.manual_step = "fetching" # fetching, analyzing, waiting, next
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

st.markdown('<div class="main-title" style="font-size: 1.8em; margin-bottom: 20px;">Automação MROSC</div>', unsafe_allow_html=True)

st.sidebar.header("⚙️ Configurações da Busca")
estado = st.sidebar.selectbox("Estado alvo (UF)", [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
], disabled=(st.session_state.running_state != "idle"))

limite = st.sidebar.slider("Limite de resultados por query", 1, 50, 10, disabled=(st.session_state.running_state != "idle"))

modo_manual = st.sidebar.checkbox("Modo Manual (Aprovação Passo a Passo)", value=False, disabled=(st.session_state.running_state != "idle"))

def safe_rerun():
    if hasattr(st, 'rerun'):
        st.rerun()
    else:
        st.experimental_rerun()

def process_manual_action(action, url, path, analysis, automator):
    if action == "approve":
        automator.process_and_save_document(url, Path(path), analysis)
        st.toast("Documento aprovado e salvo!", icon="✅")
    elif action == "skip":
        st.toast("Documento pulado.", icon="⏭️")
        
    if path and os.path.exists(path):
        try: os.unlink(path)
        except: pass
        
    st.session_state.current_idx += 1
    st.session_state.manual_step = "next"
    safe_rerun()

def render_document_review(url, path, analysis, automator, idx, total):
    st.markdown(f"### Revisando Documento {idx + 1} de {total}")
    st.markdown(f"**🔗 Fonte:** [{url}]({url})")
    
    act1, act2 = st.columns(2)
    with act1:
        if st.button("✅ Aprovar", use_container_width=True, type="primary", key=f"btn_approve_{idx}"):
            process_manual_action("approve", url, path, analysis, automator)
    with act2:
        if st.button("⏭️ Pular", use_container_width=True, key=f"btn_skip_{idx}"):
            process_manual_action("skip", url, path, analysis, automator)

    st.markdown("---")
    
    # --- VISUALIZADORES ---
    c_doc, c_ia = st.columns([1.2, 1])
    with c_doc:
        st.markdown("**Documento Original**")
        try:
            if path.endswith(".html"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    import streamlit.components.v1 as components
                    components.html(f"<div style='border: 1px solid #ccc; padding:10px; border-radius:5px; background: white;'>{content}</div>", height=600, scrolling=True)
            elif path.endswith(".pdf"):
                with open(path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf" style="border: 1px solid #ccc; border-radius:5px;"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.warning(f"Arquivo não renderizável (formato desconhecido).")
        except Exception as e:
            st.error(f"Erro ao carregar visualização: {e}")

    with c_ia:
        st.markdown("**Análise da IA**")
        
        with st.container(height=600):
            if isinstance(analysis, dict):
                if analysis.get("relevante"):
                    st.success("**Sugestão: RELEVANTE**")
                else:
                    st.error("**Sugestão: NÃO Relevante**")
                
                st.json(analysis, expanded=True)
            else:
                st.error("Falha na análise ou não obteve JSON válido.")

def reset_state():
    st.session_state.running_state = "idle"
    st.session_state.automator = None
    st.session_state.links = []
    st.session_state.current_idx = 0
    st.session_state.manual_step = "fetching"
    st.session_state.current_analysis = None
    if st.session_state.current_temp_path and os.path.exists(st.session_state.current_temp_path):
        try: os.unlink(st.session_state.current_temp_path)
        except: pass
    st.session_state.current_temp_path = None

if st.session_state.running_state == "idle":
    st.info("Configure os parâmetros na barra lateral e inicie o processo para encontrar documentos referentes ao MROSC no estado selecionado.")
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("Iniciar Automação", use_container_width=True, type="primary"):
            st.session_state.modo_manual = modo_manual
            st.session_state.running_state = "running_manual" if modo_manual else "running_auto"
            safe_rerun()

# ----------------- EXECUÇÃO AUTOMÁTICA OU MANUAL ----------------- #
if st.session_state.running_state != "idle":
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("⏹️ Parar", use_container_width=True):
            reset_state()
            safe_rerun()

    from automacao_mrosc import MROSCAutomator
    nomes_estados = {
        "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
        "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo",
        "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
        "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná",
        "PE": "Pernambuco", "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
        "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina",
        "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
    }
    nome_estado = nomes_estados.get(estado, estado)
    
    st.markdown("---")

    # MODO AUTOMÁTICO (COMO ERA ANTES)
    if st.session_state.running_state == "running_auto":
        st.markdown("**⚡ Execução Automática**")
        progress_bar = st.progress(0)
        status_text = st.empty()
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Último Arquivo Processado**")
            viewer_placeholder = st.empty()
        with col2:
            st.markdown("**Última Análise**")
            ai_placeholder = st.empty()

        if not st.session_state.automator:
            st.session_state.automator = MROSCAutomator(uf=estado, estado=nome_estado)
            
        def automator_callback(event):
            if event["type"] == "status":
                status_text.text(event["message"])
            elif event["type"] == "links_found":
                status_text.success(f"🔍 Encontrados {event['total']} links para analisar.")
            elif event["type"] == "downloading":
                pct = event["current"] / event["total"]
                progress_bar.progress(pct)
                status_text.info(f"⏳ Processando documento {event['current']} de {event['total']}... \n\nFonte: {event['url']}")
                ai_placeholder.info("⏳ Aguardando processamento da IA...")
                viewer_placeholder.info("📥 Baixando arquivo...")
            elif event["type"] == "downloaded":
                path = event["path"]
                try:
                    viewer_placeholder.empty()
                    if path.endswith(".html"):
                        with open(path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            import streamlit.components.v1 as components
                            with viewer_placeholder.container():
                                components.html(f"<div style='border: 1px solid #ccc; padding:10px; border-radius:5px;'>{content}</div>", height=450, scrolling=True)
                    elif path.endswith(".pdf"):
                        with open(path, "rb") as f:
                            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="450" type="application/pdf" style="border: 1px solid #ccc; border-radius:5px;"></iframe>'
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
                            st.success("✅ **Relevante!** Salvando...")
                        else:
                            st.warning("❌ **Não Relevante.** Descartando...")
                        st.json(analysis, expanded=False)
                    else:
                        st.error("⚠️ Falha na análise.")
            elif event["type"] == "done":
                progress_bar.progress(1.0)
                status_text.success(f"Finalizado! {event['results_count']} documentos relevantes salvos com sucesso.")
                st.balloons()
        
        st.session_state.automator.run(ui_callback=automator_callback)
        st.success("Automação em Lote concluída.")
        if st.button("Finalizar e Voltar", key="btn_finalizar"):
            reset_state()
            safe_rerun()

    # MODO MANUAL ITERATIVO
    elif st.session_state.running_state == "running_manual":
        if not st.session_state.automator:
            st.session_state.automator = MROSCAutomator(uf=estado, estado=nome_estado)
            with st.spinner("Realizando buscas na internet... (Aguarde)"):
                st.session_state.links = st.session_state.automator.searcher.collect_links()
            st.session_state.manual_step = "next"
            safe_rerun()

        automator = st.session_state.automator
        links = st.session_state.links
        idx = st.session_state.current_idx
        total = len(links)

        if idx >= total:
            st.success(f"Fim da lista! {total} documentos processados.")
            automator.output_manager.save_excel(incremental=False)
            if st.button("Concluir Processo"):
                reset_state()
                safe_rerun()
            st.stop()

        st.progress((idx) / total if total > 0 else 0)
        st.write(f"**MODO MANUAL: Processando Link {idx + 1} de {total}**")
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
                    except: pass
                    st.session_state.current_idx += 1
                    st.session_state.manual_step = "next"
                    safe_rerun()
                
                analysis = automator.processor.analyze(parts, url, automator.estado)
                st.session_state.current_analysis = analysis
                st.session_state.manual_step = "waiting"
                safe_rerun()

        if st.session_state.manual_step == "waiting":
            # Exibe o visualizador imediatamente sem precisar de modal/dialog
            render_document_review(
                url, 
                st.session_state.current_temp_path, 
                st.session_state.current_analysis, 
                automator, 
                idx, 
                total
            )

# Visualizador de Logs 
st.markdown("---")
st.markdown("**Últimos Logs**")
if os.path.exists("logs/automacao.log"):
    with open("logs/automacao.log", "r", encoding="utf-8") as f:
        lines = f.readlines()[-15:]
        st.code("".join(lines), language="text")
else:
    st.write("Nenhum log gerado ainda.")

