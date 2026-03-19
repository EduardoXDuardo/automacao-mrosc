# Automação MROSC - Coleta e Análise de Documentos

Ferramenta desenvolvida para automatizar a busca, download e catalogação de documentos normativos (decretos, leis, manuais) referentes ao MROSC (Lei nº 13.019/2014) em âmbitos estaduais e municipais.

O projeto une web scraping (DuckDuckGo) com IA (Gemini API) para analisar PDFs e páginas HTML, extraindo a relevância jurídica e consolidando os resultados em planilhas Excel estruturadas.

*Desenvolvido como parte do projeto de Iniciação Científica (PUB-USP 2025-2026) associado à pesquisa financiada pela FAPESP.*

---

## Funcionalidades

- **Busca Automatizada:** Consulta o buscador DuckDuckGo por arquivos relacionados ao MROSC em sites governamentais.
- **Scraping e Download:** Baixa PDFs e páginas web (HTML).
- **Processamento de Texto e OCR:** Lê textos via `pdfplumber` e `BeautifulSoup`. Usa `pdf2image` para extrair texto de PDFs escaneados (Diários Oficiais).
- **Análise com IA (Gemini):** Faz a triagem inteligente (se é juridicamente relevante), classifica o tipo, cria resumos e sugere um nome padronizado para o arquivo.
- **Consolidação em Excel:** Gera uma planilha `dados-compilados.xlsx` com rastreabilidade completa (links, ID único, resumos, caminho local).

---

## Pré-requisitos

1. **Python 3.9+**
2. **Chave de API do Google Gemini** (Grátis no [Google AI Studio](https://aistudio.google.com/))
3. **Poppler** (Necessário para o OCR em PDFs escaneados)

---

## Instalação

### Linux (Ubuntu/Debian)

```bash
# 1. Instale as dependências de sistema
sudo apt-get update
sudo apt-get install poppler-utils python3-venv python3-pip -y

# 2. Clone e acesse a pasta do projeto
git clone https://github.com/usuario/automacao-mrosc.git
cd automacao-mrosc

# 3. Crie o ambiente virtual e instale as dependências
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows

1. **Poppler:** Baixe a [Release build do Poppler para Windows](https://github.com/oschwartz10612/poppler-windows/releases/). Extraia o `.zip` (ex: `C:\poppler`) e adicione a pasta `bin` (ex: `C:\poppler\Library\bin`) às **Variáveis de Ambiente** do Windows (`Path`). Teste abrindo o terminal e digitando `pdftoppm -h`.
2. **Python e Dependências:**
   ```powershell
   cd automacao-mrosc
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

---

## Configuração

Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base) e adicione sua chave de API:

```env
GEMINI_API_KEY=SUA_CHAVE_AQUI
```

---

## Como Usar

Com o ambiente virtual ativado (`venv`), execute o script passando a **Sigla** e o **Nome do Estado**:

```bash
python automacao-mrosc.py <UF> "<NOME DO ESTADO>"
```

**Exemplos:**
```bash
python automacao-mrosc.py BA "Bahia"
python automacao-mrosc.py SP "São Paulo"
```

A automação vai pesquisar, baixar e analisar os documentos. Os arquivos válidos serão processados e organizados.

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