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

            df = pd.DataFrame(dados)

            st.success(f"{len(df)} colaboradores carregados")

            # 🔥 MOSTRA NA TELA
            st.dataframe(df, width="stretch", height=800)

            # 🔥 SALVA NO SHEETS
            salvar_no_sheets(dados)

            st.success("Dados enviados para o Google Sheets")

        except Exception as e:
            st.error(str(e))