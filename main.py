# -*- coding: utf-8 -*-
import re
import pdfplumber as pdfp
from pdfplumber.page import Page
import pandas as pd
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from jinja2 import Environment, FileSystemLoader

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

groq = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY,
    temperature=0,
)

csv_instrucoes = CommaSeparatedListOutputParser().get_format_instructions()
csv_output_parser = CommaSeparatedListOutputParser()
chat_template = ChatPromptTemplate.from_template(
    """Quais são os nomes femininos presentes na lista a seguir?
    responda somente os nomes: {pergunta}. \n"""
    + csv_instrucoes
)

chain = chat_template | groq | csv_output_parser

# Lista de listas para armazenar os resultados
tabela_resultado_final = []

# Dicionário para armazenar os períodos existentes na escola e seus respectivos totais de alunos
periodos = {"total": 0}
total_alunos = 0
data = ""
escola = ""
conteudo_html = ""


# Função para cortar uma página do PDF e extrair texto
def cortar_pagina(pagina: Page) -> list[str]:
    pagina_cortada = pagina.crop((0, 0, pagina.width, 0.1 * pagina.height))
    lista_texto = pagina_cortada.extract_text_simple().split("\n")
    return lista_texto


def get_dados_escola(pdf_path: str) -> tuple[str, str]:
    with pdfp.open(pdf_path) as pdf:
        primeira_pagina = pdf.pages[0]
        lista_texto = cortar_pagina(primeira_pagina)
        data = lista_texto[0]
        escola = re.search(r"Escola: .*- (.*) NR", lista_texto[2]).group(1)
        if not escola:
            st.error("Arquivo PDF inválido!")
            st.stop()
    return data, escola


def get_dados_sala(pagina: Page) -> tuple[str, str]:
    """Extrai a classe e o período de uma página PDF específica.

    Esta função recebe um objeto `pdfp.Page` como entrada, lê o texto da área recortada da página e
    extrai a classe (por exemplo, "1° ANO A") e o período (por exemplo, "TARDE") usando expressões regulares.
    Args:
        pagina (Page): A página PDF de onde extrair informações.

    Returns:
        tuple[str, str]: Uma tupla contendo a classe e o período extraídos da
                         texto da página.
    """
    lista_texto = cortar_pagina(pagina)
    sala = re.search(r"Turma: (\d° ANO \S*) ", lista_texto[4]).group(1)
    periodo = re.search(r"\s([A-Z]+)\sANUAL", lista_texto[4]).group(1)
    return sala, periodo


# Cria um dataframe contendo somente alunos ativos a partir do pdf fornecido
def criar_dataframe_ativos(tabela: list[list[str]]) -> pd.DataFrame:
    df = pd.DataFrame(tabela)
    # Seleciona as colunas relevantes e filtra apenas os alunos ativos
    df = df.iloc[1:, [2, 7]]
    df_ativos = df[df.iloc[:, 1] == "ATIVO"]
    return df_ativos


# Função para calcular a quantidade de meninos e meninas a partir de uma lista de nomes femininos
def calcular_generos(
    lista_nomes_femininos: list[str], qtd_alunos_ativos: int
) -> tuple[int, int]:
    meninas = len(lista_nomes_femininos)
    meninos = qtd_alunos_ativos - meninas
    return meninas, meninos


# função para obter os primeiros nomes de um dataframe e retornar uma lista
def get_primeiros_nomes(df: pd.DataFrame) -> list[str]:
    lista_primeiros_nomes = df[2].str.split().str[0].tolist()
    return lista_primeiros_nomes


# Função para obter os nomes das meninas utilizando a biblioteca langchain
def get_meninas(lista_nomes: list[str]) -> list[str]:
    nomes_femininos = chain.invoke({"pergunta": lista_nomes})
    return nomes_femininos


# Função para adicionar um período ao dicionário global de períodos e atualizar a quantidade total de alunos ativos
def adicionar_periodo(periodo: str, qtd_alunos_ativos: int) -> None:
    try:
        periodos[periodo] += qtd_alunos_ativos
        periodos["total"] += qtd_alunos_ativos
    except KeyError:
        periodos[periodo] = qtd_alunos_ativos
        periodos["total"] += qtd_alunos_ativos


# Função para adicionar uma linha na tabela de resultados final com os dados fornecidos
def adicionar_linha_resulta_final(
    nome_sala: str,
    periodo: str,
    qtd_alunos_ativos: int,
    qtd_meninas: int,
    qtd_meninos: int,
) -> None:
    tabela_resultado_final.append(
        [nome_sala, periodo, qtd_alunos_ativos, qtd_meninas, qtd_meninos]
    )


# Função para apresentar o resultado final em uma tabela no Streamlit
def apresentar_resultado_final(container):
    df_resultados = pd.DataFrame(
        tabela_resultado_final,
        columns=[
            "Sala",
            "Período",
            "Quantidade Total de Alunos",
            "Quantidade de Meninas",
            "Quantidade de Meninos",
        ],
    )
    container.dataframe(df_resultados, hide_index=True)


# Função para apresentar o total de alunos por período no Streamlit
def apresentar_total_alunos_por_periodo(container):
    global total_alunos
    total_alunos = periodos.pop("total")
    df_periodos = pd.DataFrame(
        list(periodos.items()), columns=["Período", "Total de Alunos"]
    )
    container.dataframe(df_periodos[["Período", "Total de Alunos"]], hide_index=True)
    container.write(f"**Total geral de alunos ativos: {total_alunos}**")


def main():
    st.title("Relatório de Alunos com IA")
    formulario = st.form("Contagem de Alunos")
    relatorio = st.container()

    with formulario:
        pdf_file = st.file_uploader("📂 **Clique abaixo para selecionar sua Lista Piloto em PDF** (Ou arraste o arquivo para a área da nuvem abaixo)", type=["pdf"])
        btn_gerar_relatorio = st.form_submit_button("Gerar Relatório")

        if btn_gerar_relatorio:
            if pdf_file is not None:
                with st.spinner("Processando o PDF..."):
                    global data, escola
                    data, escola = get_dados_escola(pdf_file)
                    relatorio.header("Totais de Alunos")
                    relatorio.write(data)
                    relatorio.write(escola)

                    with pdfp.open(pdf_file) as pdf:
                        for page in pdf.pages:
                            tabela = page.extract_table()
                            sala, periodo = get_dados_sala(page)
                            with st.spinner(f"Extraindo dados da sala: {sala}..."):
                                df_alunos_ativos = criar_dataframe_ativos(tabela)
                                qtd_ativos = len(df_alunos_ativos)
                                primeiros_nomes = get_primeiros_nomes(df_alunos_ativos)
                                nomes_femininos = get_meninas(primeiros_nomes)
                                adicionar_periodo(periodo, qtd_ativos)
                                meninas, meninos = calcular_generos(
                                    nomes_femininos, qtd_ativos
                                )
                                adicionar_linha_resulta_final(
                                    sala, periodo, qtd_ativos, meninas, meninos
                                )

                    apresentar_resultado_final(relatorio)
                    apresentar_total_alunos_por_periodo(relatorio)

                    global tabela_resultado_final, periodos, total_alunos

                    df_resultados = pd.DataFrame(
                        tabela_resultado_final,
                        columns=[
                            "Sala",
                            "Período",
                            "Quantidade Total de Alunos",
                            "Quantidade de Meninas",
                            "Quantidade de Meninos",
                        ],
                    )
                    df_periodos = pd.DataFrame(
                        list(periodos.items()), columns=["Período", "Total de Alunos"]
                    )
                    dict_resultados = df_resultados.to_dict(orient="records")
                    dict_periodos = df_periodos.to_dict(orient="records")

                    env = Environment(loader=FileSystemLoader("templates"))
                    template = env.get_template("relatorio.html")
                    conteudo_html = template.render(
                        resultados=dict_resultados,
                        periodos=dict_periodos,
                        total=total_alunos,
                        nome_escola=escola,
                        data_lista=data,
                    )

                    relatorio.download_button(
                        label="Relatório pronto! Clique para baixar",
                        data=conteudo_html,
                        file_name="relatorio-alunos.html",
                        mime="text/html",
                    )
            else:
                st.error("Por favor, carregue um arquivo PDF.")


if __name__ == "__main__":
    main()
