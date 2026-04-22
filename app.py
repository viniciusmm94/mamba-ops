import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos
from services.sheets import salvar_no_sheets

st.set_page_config(layout="wide")

st.title("Mamba Ops")

if st.button("Atualizar Colaboradores"):

    with st.spinner("Buscando dados da Pontomais..."):

        try:
            dados = listar_colaboradores_ativos()
            st.write("Dados recebidos")  # 👈 DEBUG 1

            df = pd.DataFrame(dados)
            st.write("DataFrame criado")  # 👈 DEBUG 2

            st.dataframe(df, width="stretch", height=800)

            st.write("Chamando salvar...")  # 👈 DEBUG 3

            salvar_no_sheets(dados)

            st.success("Dados salvos no Google Sheets")

        except Exception as e:
            st.error(f"Erro: {e}")