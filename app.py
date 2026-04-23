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

            # opcional: salvar no sheets
            salvar_no_sheets(dados)
            st.success("Dados enviados para o Google Sheets")

        except Exception as e:
            st.error(f"Erro ao buscar colaboradores: {str(e)}")


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

            if not dados:
                st.warning("Nenhum dado retornado para essa data")
                st.stop()

            df = pd.DataFrame(dados)

            st.success(f"{len(df)} registros encontrados")
            st.dataframe(df, width="stretch")

            # opcional: salvar no sheets
            salvar_no_sheets(dados)
            st.success("Ponto enviado para o Google Sheets")

        except Exception as e:
            st.error(f"Erro ao buscar ponto: {str(e)}")


# ==============================
# 🔹 BLOCO 3 — CONTROLE DIÁRIO
# ==============================

st.subheader("Controle Diário")

if st.button("Gerar Controle"):

    with st.spinner("Processando controle..."):
        try:
            # 🔥 independente
            colaboradores = listar_colaboradores_ativos()
            dados = resumo_ponto_por_data(data)

            if not colaboradores:
                st.error("Erro ao carregar colaboradores")
                st.stop()

            if not dados:
                st.error("Nenhum dado de ponto encontrado para a data")
                st.stop()

            resultado = registrar_controle_diario(dados, colaboradores)

            if not resultado:
                st.warning("Nenhum resultado gerado (sem atrasos/ausências)")
                st.stop()

            df = pd.DataFrame(resultado)

            st.success(f"{len(df)} registros encontrados")
            st.dataframe(df, width="stretch")

        except Exception as e:
            st.error(f"Erro ao gerar controle: {str(e)}")