import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos
from services.sheets import salvar_no_sheets  # 👈 faltava isso

st.set_page_config(layout="wide")

st.title("Mamba Ops")

if st.button("Atualizar Colaboradores"):

    with st.spinner("Buscando dados da Pontomais..."):

        try:
            dados = listar_colaboradores_ativos()
            df = pd.DataFrame(dados)

            st.success(f"{len(df)} colaboradores carregados")

            st.dataframe(df, use_container_width=True, height=800)

            # 👇 salvar dentro do try
            salvar_no_sheets(dados)

            st.success("Dados salvos no Google Sheets")

        except Exception as e:
            st.error(f"Erro: {e}")