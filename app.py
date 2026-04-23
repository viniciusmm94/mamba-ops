import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos, resumo_ponto_por_data
from services.sheets import salvar_no_sheets
from services.controle import registrar_controle_diario, encontrar_ausencia_por_periodo

st.set_page_config(layout="wide")
st.title("Controle de Pontos")

# ==============================
# 🔹 TABS PRINCIPAIS
# ==============================

tabs = st.tabs([
    "Controle",
    "Ponto",
    "Férias",
    "Colaboradores"
])

# ==============================
# 🔹 TAB 1 — COLABORADORES
# ==============================

with tabs[3]:
    st.subheader("Colaboradores")

    if st.button("Atualizar Colaboradores"):
        try:
            dados = listar_colaboradores_ativos()
            df = pd.DataFrame(dados)

            st.success(f"{len(df)} colaboradores carregados")
            st.dataframe(df, use_container_width=True)

            salvar_no_sheets(dados, sheet_name="Colaboradores")

            st.success("Dados enviados para o Google Sheets")

        except Exception as e:
            st.error(str(e))


# ==============================
# 🔹 TAB 2 — PONTO
# ==============================

with tabs[1]:
    st.subheader("Resumo de Ponto")

    data_input = st.date_input("Selecione a data", key="ponto_data")

    if st.button("Buscar Ponto"):
        try:
            data = data_input.strftime("%d/%m/%Y")

            dados = resumo_ponto_por_data(data)
            df = pd.DataFrame(dados)

            st.dataframe(df, use_container_width=True)

            salvar_no_sheets(dados, sheet_name="Resumo Ponto Hoje")

            st.success("Ponto enviado para o Google Sheets")

        except Exception as e:
            st.error(str(e))


# ==============================
# 🔹 TAB 3 — CONTROLE
# ==============================

with tabs[0]:
    st.subheader("Controle Diário")

    data_input_ctrl = st.date_input("Data para controle", key="controle_data")

    if st.button("Gerar Controle"):
        try:
            data = data_input_ctrl.strftime("%d/%m/%Y")

            colaboradores = listar_colaboradores_ativos()
            dados = resumo_ponto_por_data(data)

            resultado = registrar_controle_diario(dados, colaboradores)
            df = pd.DataFrame(resultado)

            st.success(f"{len(df)} registros encontrados")
            st.dataframe(df, use_container_width=True)

        except Exception as e:
            st.error(str(e))


# ==============================
# 🔹 TAB 4 — FÉRIAS
# ==============================

with tabs[2]:
    st.subheader("Gestão de Férias")

    from services.pontomais import get_absences, criar_ferias, editar_ausencia

    @st.cache_data
    def get_colaboradores():
        return listar_colaboradores_ativos()

    colaboradores = get_colaboradores()
    nomes = [c["Nome"] for c in colaboradores]

    nome_sel = st.selectbox("Selecionar colaborador", nomes)
    emp = next(c for c in colaboradores if c["Nome"] == nome_sel)

# ==============================
# 🔹 VISUALIZAR FÉRIAS
# ==============================

st.markdown("### Férias atuais")

with st.spinner("Carregando dados..."):
    absences = get_absences(emp["ID"])

if absences:
    df_abs = pd.DataFrame(absences)

    colunas_desejadas = [
        "id",
        "start_date",
        "end_date",
        "observation",
        "total_days"
    ]

    df_abs = df_abs[[c for c in colunas_desejadas if c in df_abs.columns]]

    df_abs = df_abs.rename(columns={
        "id": "ID",
        "start_date": "Início",
        "end_date": "Fim",
        "observation": "Tipo",
        "total_days": "Dias"
    })

    st.dataframe(df_abs, use_container_width=True)

else:
    st.markdown(
        """
        <div style="
            background-color: rgb(197, 180, 96);
            border: 1px solid rgba(0,0,0,0.1);
            padding: 8px 12px;
            border-radius: 6px;
            color: #333;
            font-size: 13px;
            margin-top: -8px;
            margin-bottom: 8px;
        ">
            Nenhuma ausência encontrada
        </div>
        """,
        unsafe_allow_html=True
    )

# 🔥 FORA DO IF/ELSE
st.divider()

col1, col2 = st.columns(2)