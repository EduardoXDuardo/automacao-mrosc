# Automação MROSC - Coleta e Análise de Documentos

Este projeto foi desenvolvido como parte do projeto de Iniciação Científica (PUB-USP 2025-2026) associado à pesquisa financiada pela FAPESP: *"Capacidades Estatais para a Implementação do Marco Regulatório das Organizações da Sociedade Civil: parcerias entre OSCs e a Gestão Pública"*. 

A ferramenta foi idealizada para apoiar a frente de **coleta de dados qualitativos e quantitativos**, automatizando a busca, o download, a leitura e a catalogação de documentos normativos (decretos, leis, manuais) estaduais e municipais referentes ao MROSC (Lei nº 13.019/2014).

O script une web scraping guiado (via DuckDuckGo) com Inteligência Artificial (Gemini API) para analisar o conteúdo de PDFs e páginas HTML, extraindo a relevância jurídica do documento e consolidando os resultados analisados em planilhas Excel estruturadas para a pesquisa.

---

## 🚀 Funcionalidades

- **Busca Automatizada:** Consulta o buscador DuckDuckGo com base no estado solicitado, procurando arquivos relacionados ao MROSC.
- **Scraping e Download Multiformato:** Identifica e baixa tanto arquivos PDF quanto páginas web (HTML), lidando de forma resiliente com erros de requisição.
- **Processamento de Texto e OCR:** Lê textos dos documentos utilizando `pdfplumber` e `BeautifulSoup`. Caso encontre PDFs escaneados (sem texto selecionável), aplica conversão de PDF para imagem (`pdf2image`) para que a IA consiga extrair o texto visualmente.
- **Integração com IA (Gemini):** Efetua uma triagem inteligente. A IA decide se o documento é juridicamente relevante, classifica o tipo (ex: Lei, Decreto, Manual), cria resumos (considerações) e sugere um nome limpo para o arquivo.
- **Consolidação dos Dados:** Gera automaticamente uma tabela no Excel (`dados-compilados.xlsx`) com toda a rastreabilidade (links, id único, resumos, etc) e renomeia os arquivos para um formato padrão, organizando-os em uma pasta hierárquica por data e estado.

---

## 📋 Pré-requisitos Gerais

Para rodar este raspador e analisador, você precisará de:
1. **Python 3.9 ou superior** instalado em sua máquina.
2. **Chave de API do Google Gemini** (Você deve gerar gratuitamente no [Google AI Studio](https://aistudio.google.com/)).
3. **Poppler** (Uma biblioteca de sistema operacional necessária para ler páginas de PDFs como imagens - vital para lidar com Diários Oficiais escaneados).

---

## 💻 Instalação - Guia Detalhado

Siga o tutorial correspondente ao seu sistema operacional para configurar o ambiente com perfeição.

### 🐧 No Linux (Ubuntu/Debian)

As distribuições Linux tornam a instalação das dependências de sistema muito simples. Siga os passos no terminal:

1. **Instale as dependências de sistema (Poppler e Venv):**
   ```bash
   sudo apt-get update
   sudo apt-get install poppler-utils python3-venv python3-pip -y
   ```

2. **Clone/Navegue até a pasta do projeto:**
   ```bash
   cd ~/Github/automacao-mrosc  # Modifique para o seu caminho real
   ```

3. **Crie e ative o ambiente virtual (Recomendado):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Instale as bibliotecas Python necessárias:**
   ```bash
   pip install -r requirements.txt
   ```

### 🪟 No Windows

No Windows, a etapa mais crítica é a instalação do `Poppler`. Siga minuciosamente os passos:

1. **Instalação do Poppler:**
   - Faça o download da versão mais recente do Poppler para Windows [neste link (Release build)](https://github.com/oschwartz10612/poppler-windows/releases/). (Baixe o arquivo `.zip`).
   - Extraia o conteúdo do zip, por exemplo para `C:\poppler`.
   - Adicione o diretório `bin` do Poppler nas **Variáveis de Ambiente** do seu Windows (O caminho será algo como `C:\poppler\Library\bin`).
   - *Dica:* Para verificar se funcionou, abra um novo terminal (PowerShell ou CMD) e digite `pdftoppm -h`. Se não der erro ("comando não reconhecido"), deu certo.

2. **Abra o terminal (PowerShell) e navegue até a pasta do projeto:**
   ```powershell
   cd C:\Sua\Pasta\Para\O\Projeto\automacao-mrosc
   ```

3. **Crie e ative o ambiente virtual:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

4. **Instale as bibliotecas Python necessárias:**
   ```powershell
   pip install -r requirements.txt
   ```

---

## ⚙️ Configuração

Antes de executar, você precisa configurar a chave de acesso do Gemini. 

1. Na raiz da pasta do projeto, o arquivo se chama `.env`. Se ele não existir, crie um baseado em `.env.example`.
2. Insira a sua chave de API nele respeitando a formatação, conforme o modelo abaixo:

**Exemplo do `.env`:**
```env
# Configurações de API
GEMINI_API_KEY=AIzA_SUA_CHAVE_AQUI

# Configurações de Execução (Opcional)
MAX_THREADS=3
TIMEOUT=15
```

---

## ▶️ Como Usar (Executando a Automação)

A automação é operada totalmente por linha de comando. Após estar com o ambiente virtual ativado (o `(venv)` deve aparecer no seu terminal), execute o script passando **dois parâmetros**: a Sigla do Estado e o Nome Completo do Estado.

**Estrutura do comando:**
```bash
python automacao-mrosc.py <UF> "<NOME DO ESTADO>"
```

**Exemplos Páticos:**

*Buscando informações da Bahia:*
```bash
python automacao-mrosc.py BA "Bahia"
```

*Buscando informações de São Paulo:*
```bash
python automacao-mrosc.py SP "São Paulo"
```

*Buscando informações de Minas Gerais:*
```bash
python automacao-mrosc.py MG "Minas Gerais"
```

### O que acontece durante a execução?

1. O script vai pesquisar variações de termos baseados no estado (ex: `site:sp.gov.br "13.019" decreto`).
2. Irá baixar cópias temporárias na pasta `output/XX_ANOMESDIA_HORA/`.
3. O Gemini analisará página por página extraída.
4. Os arquivos julgados pelo modelo como sendo "Decretos, Manuais, Portarias ou normativas" serão avaliados, renomeados, e guardados.

---

## 📂 Estrutura de Retorno (Output)

Ao final do processamento, vá para o diretório de `output`. O sistema terá gerado uma pasta com o timestamp do andamento. Dentro dela:

```text
output/
└── SP_20260318_191724/                  # Pasta gerada dinamicamente
    ├── archives/                        # Documentos renomeados e limpos
    │   ├── SP01_Decreto_Estadual_61981.pdf
    │   └── SP02_Manual_Parcerias_OSC.html
    └── dados-compilados.xlsx            # SUA PLANILHA PRONTA!
```

A **planilha do Excel** conterá colunas como: Unidade Federativa, Código de Rastreabilidade, Tipo de normativo, Título identificado, Link original, um Resumo/Consideração elaborado pela IA, e o Endereço local onde o documento foi salvo.

---

## 👨‍💻 Contribuidores e Contexto Acadêmico

- **Pesquisador Bolsista:** Luiz Eduardo da Silva (PUB-USP / EACH)
- **Orientadora:** Profa. Dra. Patricia Maria Emerenciano de Mendonça
- **Contexto:** Este sistema corrobora com a diretriz do projeto FAPESP, suportando "a automatização de buscas de documentos que serão usados para acesso a dados secundários da pesquisa, tais como: [...] Leis, decretos e regulamentos relacionados ao MROSC inclusive regulamentações estaduais e municipais".
