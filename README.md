# 📚 Contagem de Alunos e Análise de Gênero com IA

Este é uma aplicação Streamlit desenvolvida para automatizar a extração e análise de dados de listas de chamadas escolares em formato PDF. O sistema processa o arquivo, contabiliza alunos ativos e utiliza Inteligência Artificial (LLM) para realizar a distinção de gênero baseado nos nomes dos alunos.

## ⚙️ Funcionalidades

- **Processamento de PDF:** Lê arquivos PDF contendo listas de turmas.
- **Extração de Dados:** Identifica automaticamente:
  - Nome da Escola
  - Data da lista
  - Turmas e Períodos (Manhã/Tarde/Etc)
  - Alunos com situação "ATIVO"
- **Classificação de Gênero com IA:** Utiliza a API da Groq (modelo `llama-3.3-70b-versatile`) e LangChain para identificar nomes femininos e calcular a proporção de meninos e meninas.
- **Visualização de Dados:** Exibe tabelas com totais por sala e por período diretamente na interface.
- **Relatório HTML:** Gera e permite o download de um relatório HTML formatado (usando Jinja2) com todos os dados compilados.

## 🛠️ Tecnologias Utilizadas

- **Python 3**
- **Streamlit** - Interface Web
- **PDFPlumber** - Extração de texto e tabelas de PDFs
- **Pandas** - Manipulação de dados
- **LangChain** - Orquestração de LLMs
- **Groq API** - Motor de inferência de IA ultra-rápido
- **Jinja2** - Motor de templates para relatório HTML

## 🔧 Pré-requisitos

Antes de começar, você precisará ter o Python instalado e uma chave de API da Groq.

### 1. Clonar o repositório
```bash
git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
cd seu-repositorio
```

### 2. Instalar as dependências

Você pode instalar as dependências de duas formas:

#### Opção A: Usando pip (ambiente virtual recomendado)

Crie um arquivo `requirements.txt` (se não houver) com o seguinte conteúdo e instale:
```
streamlit
pdfplumber
pandas
langchain-groq
langchain-core
jinja2
```

Comando de instalação:
```bash
pip install -r requirements.txt
```

#### Opção B: Usando Conda (recomendado)

Se você utiliza a distribuição Anaconda ou Miniconda, pode criar o ambiente diretamente a partir do arquivo `environment.yml`:
```bash
conda env create -f environment.yml
```

Após a criação do ambiente, ative-o:
```bash
conda activate nome-do-ambiente
```

**Nota:** O nome do ambiente será definido no arquivo `environment.yml`. Verifique a primeira linha do arquivo para identificar o nome correto.

Para atualizar um ambiente existente com novas dependências:
```bash
conda env update -f environment.yml --prune
```

### 3. Configurar a API Key (Secreta)

O projeto utiliza o gerenciamento de segredos do Streamlit. Você deve criar um arquivo de configuração local.

1. Crie uma pasta chamada `.streamlit` na raiz do projeto.
2. Dentro dela, crie um arquivo chamado `secrets.toml`.
3. Adicione sua chave da Groq no arquivo:
```toml
# .streamlit/secrets.toml
GROQ_API_KEY = "gsk-..."
```

**Nota:** Nunca suba o arquivo `secrets.toml` para o GitHub.

## 📁 Estrutura de Arquivos Esperada

Para que o gerador de relatórios funcione corretamente, certifique-se de que a estrutura de pastas seja semelhante a esta:
```
/
├── main.py                  # Código principal da aplicação
├── templates/
│   └── relatorio.html       # Template Jinja2 para o relatório final
├── .streamlit/
│   └── secrets.toml         # Chave de API (não versionar)
├── requirements.txt         # Dependências para pip
├── environment.yml          # Dependências para conda
└── README.md
```

## 📘 Como Executar

Na raiz do projeto, execute o comando:
```bash
streamlit run main.py
```

O navegador abrirá automaticamente no endereço `http://localhost:8501`.

## 📄 Formato do PDF Suportado

O script foi desenhado para um layout específico de relatório escolar. Ele espera encontrar padrões como:

- **Escola:** `(^a ANO \d+)`
- Uma tabela onde a coluna 2 contém os nomes e a coluna 7 contém a situação (ex: "ATIVO").


## 📜 Licença

Este projeto está sob a licença MIT.