# Automação MROSC - Coleta e Análise de Documentos

Ferramenta desenvolvida para automatizar a busca, download e catalogação de documentos normativos (decretos, leis, manuais) referentes ao MROSC (Lei nº 13.019/2014) em âmbitos estaduais e municipais.

O projeto une web scraping (DuckDuckGo) com IA (Gemini API) para analisar PDFs e páginas HTML, extraindo a relevância jurídica e consolidando os resultados em planilhas Excel estruturadas.

*Desenvolvido como parte do projeto de Iniciação Científica (PUB-USP 2025-2026) associado à pesquisa financiada pela FAPESP.*

---

## Funcionalidades

- **Interface Web (UI):** Painel interativo integrado via Streamlit para configurar e rodar as extrações direto do navegador.
- **Dockerizado:** Imagem Docker pronta para rodar em qualquer VPS ou PC local sem configurações complexas de dependências.
- **Busca Automatizada:** Consulta o buscador DuckDuckGo por arquivos relacionados ao MROSC em sites governamentais.
- **Scraping e Download:** Baixa PDFs e páginas web (HTML) com tratamento seguro de SSL.
- **Processamento:** Extrai nativamente conteúdo de arquivos diretamente do Gemini 1.5, garantindo leitura total confiável e rápida, operando de forma simultânea.
- **Análise com IA (Gemini):** Faz a triagem inteligente (se é juridicamente relevante), classifica o tipo, cria resumos e sugere um nome padronizado.
- **Sistema de Logs Estruturado:** Monitoramento contínuo da execução salvo automaticamente em `logs/automacao.log`.
- **Consolidação em Excel:** Gera uma planilha `dados-compilados.xlsx` com rastreabilidade completa.

---

## Pré-requisitos

- **Docker e Docker Compose** instalados na sua máquina (Método Recomendado).
- Alternativamente (Método Local): Python 3.9+ configurado.
- **Chave de API do Google Gemini** (Grátis no [Google AI Studio](https://aistudio.google.com/)).

---

## Instalação e Configuração

Crie um arquivo `.env` na raiz do projeto e adicione sua chave de API:

```env
GEMINI_API_KEY=SUA_CHAVE_AQUI
```

### Método 1: Usando Docker (Recomendado)
A forma mais fácil de rodar o projeto e a interface de usuário, pois configura todas as dependências do sistema operacionais (Python e Poppler) automaticamente.

1. Faça o build da imagem:
```bash
docker build -t automacao-mrosc .
```
2. Rode o container:

**No Linux/Mac ou PowerShell:**
```bash
docker run -p 8501:8501 -v "${PWD}/output:/app/output" -v "${PWD}/logs:/app/logs" -v "${PWD}/.env:/app/.env" automacao-mrosc
```

**No Git Bash (Windows):**
```bash
docker run -p 8501:8501 -v "/$(pwd)/output:/app/output" -v "/$(pwd)/logs:/app/logs" -v "/$(pwd)/.env:/app/.env" automacao-mrosc
```

### Método 2: Instalação Manual (Local)

#### Windows
1. Crie o ambiente virtual e instale as dependências:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update && sudo apt-get install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Como Usar

### Opção 1: Via Interface Web (Streamlit)
Com o ambiente ativado (ou rodando o Docker do Método 1), execute:
```bash
streamlit run app.py
```
Acesse `http://localhost:8501` no navegador. Pela interface é possível escolher o Estado e acompanhar os logs de extração.

### Opção 2: Via Terminal (CLI)
Com o ambiente virtual ativado (`venv`), execute o script clássico passando a **Sigla** e o **Nome do Estado**:

```bash
python automacao_mrosc.py <UF> "<NOME DO ESTADO>"
```

**Exemplo:**
```bash
python automacao_mrosc.py BA "Bahia"
```

A automação vai pesquisar, baixar e analisar os documentos em background.

---

## Estrutura de Saída (Output)

Os resultados ficam salvos na pasta `output/`, organizados por estado e data de execução:

```text
output/
└── SP_20260318_191724/                  
    ├── archives/                        # Documentos em PDF/HTML limpos e renomeados
    │   ├── SP01_Decreto_Estadual.pdf
    │   └── SP02_Manual_Parcerias.html
    └── dados-compilados.xlsx            # Planilha final com todos os metadados
```

---

## Créditos

- **Pesquisador Bolsista:** Luiz Eduardo da Silva (PUB-USP / EACH)
- **Orientadora:** Profa. Dra. Patricia Maria Emerenciano de Mendonça