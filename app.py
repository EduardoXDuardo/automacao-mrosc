import streamlit as st
import os
import time
import base64
import shutil
from pathlib import Path
from config import logger 

st.set_page_config(page_title="Automação MROSC", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .header-container {
        padding: 40px 20px 30px 20px;
        text-align: center;
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 16px;
        margin-bottom: 40px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        color: white;
    }
    .main-title {
        color: white;
        font-weight: 800;
        font-size: 3rem;
        margin: 0;
        letter-spacing: -1.5px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 1.15rem;
        font-weight: 400;
        margin-top: 10px;
        margin-bottom: 0;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
    }
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px -1px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    }
    .stButton>button[kind="secondary"] {
        background: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
    }
    .stButton>button[kind="secondary"]:hover {
        background: #e2e8f0;
        transform: translateY(-2px);
    }
    
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
        border-right: 1px solid #e2e8f0;
    }
    [data-testid="stSidebar"] * {
        color: #0f172a;
    }

    div.stMetric {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px 25px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetricValue"] {
        color: #2563eb;
        font-weight: 800;
        font-size: 2.2rem;
    }
    div[data-testid="stMetricLabel"] {
        color: #64748b;
        font-weight: 500;
        font-size: 1rem;
    }
    
    .terminal-log {
        background-color: #0f172a;
        color: #10b981;
        padding: 20px;
        border-radius: 12px;
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 0.9em;
        height: 350px;
        overflow-y: auto;
        white-space: pre-wrap;
        box-shadow: inset 0 4px 6px rgba(0, 0, 0, 0.3);
        border: 1px solid #1e293b;
        line-height: 1.6;
    }
    .terminal-log span.error { color: #ef4444; font-weight: bold; }
    .terminal-log span.info { color: #3b82f6; }
    .terminal-log span.warning { color: #f59e0b; }
    
    .doc-viewer {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0;
        background: #ffffff;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        overflow: hidden;
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

st.markdown('''
<div class="header-container">
    <div class="main-title">Automação MROSC</div>
    <div class="sub-title">Inteligência Artificial Direcionada a Documentos e Parcerias Públicas</div>
</div>
''', unsafe_allow_html=True)

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3214/3214746.png", width=60)
st.sidebar.markdown("### ⚙️ Painel de Controle")
st.sidebar.markdown("Configure os filtros abaixo:")
estado = st.sidebar.selectbox("Estado alvo (UF)", [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", 
    "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", 
    "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
], disabled=(st.session_state.running_state != "idle"))

limite = st.sidebar.slider("Limite de resultados por query", 1, 50, 10, disabled=(st.session_state.running_state != "idle"))

modo_manual = st.sidebar.checkbox("Modo Manual (Aprovação Passo a Passo)", value=False, disabled=(st.session_state.running_state != "idle"))

def safe_rerun():
    st.rerun()

def process_manual_action(action, url, path, analysis, automator):
    if action == "approve":
        automator.process_and_save_document(url, Path(path), analysis)
        st.toast("Documento aprovado e salvo!")
    elif action == "skip":
        st.toast("Documento pulado.")
        
    if path and os.path.exists(path):
        try: os.unlink(path)
        except: pass
        
    st.session_state.current_idx += 1
    st.session_state.manual_step = "next"
    safe_rerun()

def render_document_review(url, path, analysis, automator, idx, total):
    st.markdown(f"### 📄 Analisando Documento {idx + 1} de {total}")
    st.markdown(f"**Fonte Original:** [{url}]({url})")
    
    act1, act2 = st.columns(2)
    with act1:
        if st.button("✅ Aprovar & Salvar", use_container_width=True, type="primary", key=f"btn_approve_{idx}"):
            process_manual_action("approve", url, path, analysis, automator)
    with act2:
        if st.button("⏭️ Pular/Descartar", use_container_width=True, key=f"btn_skip_{idx}"):
            process_manual_action("skip", url, path, analysis, automator)

    st.markdown("---")
    
    # --- VISUALIZADORES ---
    c_doc, c_ia = st.columns([1.4, 1])
    with c_doc:
        st.markdown("#### Visualização do Documento")
        try:
            if path.endswith(".html"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    import streamlit.components.v1 as components
                    components.html(f"<div class='doc-viewer' style='height:600px; padding:15px; overflow-y:auto;'>{content}</div>", height=600, scrolling=True)
            elif path.endswith(".pdf"):
                with open(path, "rb") as f:
                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf" class="doc-viewer"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.info(f"O arquivo `{path}` foi baixado com sucesso, mas este formato não é renderizado diretamente.")
        except Exception as e:
            st.error(f"Erro ao carregar visualização: {e}")

    with c_ia:
        st.markdown("#### 🤖 Análise da Inteligência Artificial")
        
        with st.container(height=600):
            if isinstance(analysis, dict):
                if analysis.get("relevante"):
                    st.success("✅ **Recomendação: RELEVANTE**")
                else:
                    st.error("❌ **Recomendação: NÃO RELEVANTE**")
                
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
        except: pass
    st.session_state.current_temp_path = None

if st.session_state.running_state == "idle":
    st.info("ℹ️ **Bem-vindo ao Automação MROSC.**\n\nEste sistema utiliza IA para buscar e classificar editais, parcerias, pautas, relatórios e manuais do MROSC na página dos estados listados. Configure os parâmetros na aba lateral esquerda e clique em **Iniciar Automação** para começar.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_btn, _ = st.columns([1, 2])
    with col_btn:
        if st.button("🚀 Iniciar Automação", use_container_width=True, type="primary"):
            # Setup log path correctly
            os.makedirs("logs", exist_ok=True)
            if not os.path.exists("logs/automacao.log"):
                open("logs/automacao.log", "w", encoding="utf-8").close()
                
            st.session_state.modo_manual = modo_manual
            st.session_state.running_state = "running_manual" if modo_manual else "running_auto"
            safe_rerun()

# ----------------- EXECUÇÃO AUTOMÁTICA OU MANUAL ----------------- #
if st.session_state.running_state != "idle":
    st.markdown("---")
    col1, col_stop = st.columns([4, 1])
    with col_stop:
        if st.button("🛑 Parar Execução", use_container_width=True, type="secondary"):
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
        st.markdown("---")
        st.markdown('<h3>Execução Automática em Andamento</h3>', unsafe_allow_html=True)
        
        # Area for metrics
        m1, m2, m3 = st.columns(3)
        metric_total = m1.empty()
        metric_current = m2.empty()
        metric_saved = m3.empty()
        
        metric_total.metric("Links Encontrados", "0")
        metric_current.metric("Processando Agora", "0 / 0")
        metric_saved.metric("Documentos Salvos", "0")
        
        st.markdown("---")
        progress_bar = st.progress(0)
        status_text = st.empty()
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Último Arquivo Processado")
            viewer_placeholder = st.empty()
        with col2:
            st.markdown("#### Última Análise da IA")
            ai_placeholder = st.empty()

        if not st.session_state.automator:
            st.session_state.automator = MROSCAutomator(uf=estado, estado=nome_estado)
            
        def automator_callback(event):
            try:
                if event["type"] == "status":
                    status_text.info(f"**Status:** {event['message']}")
                elif event["type"] == "links_found":
                    metric_total.metric("Links Encontrados", event['total'])
                    status_text.success(f"Busca finalizada. {event['total']} links encontrados na web.")
                elif event["type"] == "downloading":
                    pct = event["current"] / event["total"]
                    progress_bar.progress(pct)
                    metric_current.metric("Processando Agora", f"{event['current']} / {event['total']}")
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
                                import streamlit.components.v1 as components
                                with viewer_placeholder.container():
                                    components.html(f"<div style='border: 1px solid #e2e8f0; padding:15px; border-radius:8px; background: white; box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06); height: 500px; overflow-y: auto;'>{content}</div>", height=520, scrolling=False)
                        elif path.endswith(".pdf"):
                            with open(path, "rb") as f:
                                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="520" type="application/pdf" style="border: 1px solid #e2e8f0; border-radius:8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);"></iframe>'
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
                    metric_saved.metric("Documentos Salvos", f"{saved_count}")
                elif event["type"] == "done":
                    progress_bar.progress(1.0)
                    status_text.success(f"**Finalizado!** {event['results_count']} documentos relevantes salvos com sucesso.")
                
                if 'log_placeholder' in st.session_state and os.path.exists("logs/automacao.log"):
                    with open("logs/automacao.log", "r", encoding="utf-8") as f:
                        lines = f.readlines()[-30:]
                        log_content = "".join(lines)
                        # Syntax hl for logs
                        formatted = log_content.replace("INFO", "<span class='info'>[INFO]</span>")\
                                               .replace("ERROR", "<span class='error'>[ERROR]</span>")\
                                               .replace("WARNING", "<span class='warning'>[WARNING]</span>")
                        st.session_state.log_placeholder.markdown(
                            f"<div class='terminal-log'>{formatted}</div>", 
                            unsafe_allow_html=True
                        )

            except Exception as callback_err:
                pass # Previne falhas de context no streamlit de travarem a automação
        
        st.markdown("---")
        st.markdown("### Diário de Execução (Tempo Real)")
        st.session_state.log_placeholder = st.empty()
        
        if os.path.exists("logs/automacao.log"):
            with open("logs/automacao.log", "r", encoding="utf-8") as f:
                lines = f.readlines()[-30:]
                log_content = "".join(lines)
                formatted = log_content.replace("INFO", "<span class='info'>[INFO]</span>")\
                                       .replace("ERROR", "<span class='error'>[ERROR]</span>")\
                                       .replace("WARNING", "<span class='warning'>[WARNING]</span>")
                st.session_state.log_placeholder.markdown(f"<div class='terminal-log'>{formatted}</div>", unsafe_allow_html=True)
        st.markdown("---")

        st.session_state.automator.run(ui_callback=automator_callback)
        st.success("Automação em Lote concluída.")
        
        base_dir = st.session_state.automator.output_manager.base_dir
        if base_dir and os.path.exists(base_dir):
            zip_path = str(base_dir) + ".zip"
            if not os.path.exists(zip_path):
                shutil.make_archive(str(base_dir), 'zip', str(base_dir))
            
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="Baixar Resultados (.zip)",
                    data=f,
                    file_name=os.path.basename(zip_path),
                    mime="application/zip"
                )

        if st.button("🏁 Finalizar e Voltar", key="btn_finalizar", type="primary"):
            reset_state()
            safe_rerun()

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
            base_dir = automator.output_manager.base_dir
            if base_dir and os.path.exists(base_dir):
                zip_path = str(base_dir) + ".zip"
                if not os.path.exists(zip_path):
                    shutil.make_archive(str(base_dir), 'zip', str(base_dir))
                
                with open(zip_path, "rb") as f:
                    st.download_button(
                        label="Baixar Resultados (.zip)",
                        data=f,
                        file_name=os.path.basename(zip_path),
                        mime="application/zip"
                    )
            if st.button("🏁 Concluir Processo", type="primary"):
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
if st.session_state.running_state == "idle":
    st.markdown("---")
    st.markdown("### Histórico de Execução (Logs)")
    if os.path.exists("logs/automacao.log"):
        with open("logs/automacao.log", "r", encoding="utf-8") as f:
            # Pega as últimas 30 linhas
            lines = f.readlines()[-30:]
            log_content = "".join(lines)
            formatted = log_content.replace("INFO", "<span class='info'>[INFO]</span>")\
                                   .replace("ERROR", "<span class='error'>[ERROR]</span>")\
                                   .replace("WARNING", "<span class='warning'>[WARNING]</span>")
            
            st.markdown(f"<div class='terminal-log'>{formatted}</div>", unsafe_allow_html=True)
        
        # Botão para limpar logs antigos
        if st.button("Limpar Histórico de Logs"):
            open("logs/automacao.log", "w").close()
            st.rerun()
    else:
        st.info("Nenhum log gerado ainda.")

