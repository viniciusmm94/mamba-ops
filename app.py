import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos, resumo_ponto_por_data
from services.sheets import salvar_no_sheets

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

            # 🔥 salva na aba correta
            salvar_no_sheets(dados, "Colaboradores")

            st.success("Dados enviados para o Google Sheets")

        except Exception as e:
            st.error(str(e))


# ==============================
# 🔹 BLOCO 2 — PONTO POR DATA
# ==============================

st.subheader("Resumo de Ponto por Data")

# 🔥 melhor UX (evita erro de digitação)
data_input = st.date_input("Selecione a data")

# converte para formato esperado
data = data_input.strftime("%d/%m/%Y")

if st.button("Buscar Ponto"):

    with st.spinner("Buscando dados de ponto..."):
        try:
            dados = resumo_ponto_por_data(data)
            df = pd.DataFrame(dados)

            st.dataframe(df, width="stretch")

            # 🔥 salva na aba correta
            salvar_no_sheets(dados, "Resumo Ponto Hoje")

            st.success("Ponto enviado para o Google Sheets")

        except Exception as e:
            st.error(str(e))

            st.write(type(dados))
            st.write(dados[:2])