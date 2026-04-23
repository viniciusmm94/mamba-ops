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

            # 🔥 salva no estado
            st.session_state["colaboradores"] = dados

            st.success(f"{len(df)} colaboradores carregados")
            st.dataframe(df, width="stretch", height=800)

            salvar_no_sheets(dados)
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

            # 🔥 salva no estado
            st.session_state["resumo"] = dados

            st.dataframe(df, width="stretch")

            salvar_no_sheets(dados)
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

            # 🔥 usa cache do app
            colaboradores = st.session_state.get("colaboradores")
            dados = st.session_state.get("resumo")

            if not colaboradores:
                st.error("Atualize os colaboradores primeiro")
                st.stop()

            if not dados:
                st.error("Busque o ponto primeiro")
                st.stop()

            resultado = registrar_controle_diario(dados, colaboradores)

            df = pd.DataFrame(resultado)

            st.success(f"{len(df)} registros encontrados")
            st.dataframe(df, width="stretch")

        except Exception as e:
            st.error(str(e))