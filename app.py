import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos, resumo_ponto_por_data
from services.sheets import salvar_no_sheets
from services.controle import registrar_controle_diario

st.set_page_config(layout="wide")
st.title("Mamba Ops")

# ==============================
# 🔹 BLOCO 1 — COLABORADORES
# ==============================

st.subheader("Colaboradores")

if st.button("Atualizar Colaboradores"):

    with st.spinner("Buscando dados da Pontomais..."):
        try:
            dados = listar_colaboradores_ativos()
            df = pd.DataFrame(dados)

            st.success(f"{len(df)} colaboradores carregados")
            st.dataframe(df, width="stretch", height=800)

            salvar_no_sheets(dados, sheet_name="Colaboradores")

            st.success("Dados enviados para o Google Sheets")

        except Exception as e:
            st.error(str(e))


# ==============================
# 🔹 BLOCO 2 — PONTO POR DATA
# ==============================

st.subheader("Resumo de Ponto por Data")

data_input = st.date_input("Selecione a data")
data = data_input.strftime("%d/%m/%Y")

if st.button("Buscar Ponto"):

    with st.spinner("Buscando dados de ponto..."):
        try:
            dados = resumo_ponto_por_data(data)
            df = pd.DataFrame(dados)

            st.dataframe(df, width="stretch")

            salvar_no_sheets(dados, sheet_name="Resumo Ponto Hoje")

            st.success("Ponto enviado para o Google Sheets")

        except Exception as e:
            st.error(str(e))


# ==============================
# 🔹 BLOCO 3 — CONTROLE DIÁRIO
# ==============================

st.subheader("Controle Diário")

if st.button("Gerar Controle"):

    with st.spinner("Processando controle..."):
        try:
            colaboradores = listar_colaboradores_ativos()
            dados = resumo_ponto_por_data(data)

            resultado = registrar_controle_diario(dados, colaboradores)

            df = pd.DataFrame(resultado)

            st.success(f"{len(df)} registros encontrados")
            st.dataframe(df, width="stretch")

        except Exception as e:
            st.error(str(e))


            st.subheader("Cadastrar Férias Manual")

nome = st.text_input("Nome completo")
inicio = st.date_input("Data início", key="inicio")
fim = st.date_input("Data fim", key="fim")

if st.button("Salvar Férias"):

    try:
        from services.sheets import append_row

        append_row("Ferias Manual", [
            nome,
            inicio.strftime("%d/%m/%Y"),
            fim.strftime("%d/%m/%Y")
        ])

        st.success("Férias cadastradas")

    except Exception as e:
        st.error(str(e))

        st.subheader("Lançar Férias")

colaboradores = listar_colaboradores_ativos()

nomes = [c["Nome"] for c in colaboradores]

nome_selecionado = st.selectbox("Selecionar colaborador", nomes)

inicio = st.date_input("Data início férias", key="ferias_inicio")
fim = st.date_input("Data fim férias", key="ferias_fim")

if st.button("Cadastrar Férias"):

    try:
        # 🔥 encontra ID
        emp = next(c for c in colaboradores if c["Nome"] == nome_selecionado)

        from services.pontomais import criar_ferias

        criar_ferias(
            employee_id=emp["ID"],
            inicio=inicio.strftime("%d/%m/%Y"),
            fim=fim.strftime("%d/%m/%Y")
        )

        st.success("Férias cadastradas com sucesso")

    except Exception as e:
        st.error(str(e))
