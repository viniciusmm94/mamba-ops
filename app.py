import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos

st.set_page_config(layout="wide")

st.title("Mamba Ops")

if st.button("Atualizar Colaboradores"):

    with st.spinner("Buscando dados da Pontomais..."):

        try:
            dados = listar_colaboradores_ativos()

            df = pd.DataFrame(dados)

            st.success(f"{len(df)} colaboradores carregados")

            st.dataframe(df, use_container_width=True, height=800)

        except Exception as e:
            st.error(str(e))