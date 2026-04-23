import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos, resumo_ponto_por_data
from services.sheets import salvar_no_sheets
from services.controle import registrar_controle_diario, encontrar_ausencia_por_periodo

st.set_page_config(layout="wide")
st.title("Mamba Ops")

# ==============================
# 🔹 TABS PRINCIPAIS
# ==============================

tabs = st.tabs([
    "Colaboradores",
    "Ponto",
    "Controle",
    "Férias"
])

# ==============================
# 🔹 TAB 1 — COLABORADORES
# ==============================

with tabs[0]:
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

with tabs[2]:
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

with tabs[3]:
    st.subheader("Gestão de Férias")

    colaboradores = listar_colaboradores_ativos()
    nomes = [c["Nome"] for c in colaboradores]

    col1, col2 = st.columns(2)

    # 🔹 CADASTRAR FÉRIAS
    with col1:
        st.markdown("### Cadastrar Férias")

        nome_create = st.selectbox("Colaborador", nomes, key="create_nome")

        inicio_api = st.date_input("Início", key="api_inicio")
        fim_api = st.date_input("Fim", key="api_fim")

        if st.button("Cadastrar Férias"):
            try:
                from services.pontomais import criar_ferias

                emp = next(c for c in colaboradores if c["Nome"] == nome_create)

                criar_ferias(
                    employee_id=emp["ID"],
                    inicio=inicio_api.strftime("%d/%m/%Y"),
                    fim=fim_api.strftime("%d/%m/%Y")
                )

                st.success("Férias cadastradas com sucesso")

            except Exception as e:
                st.error(str(e))


    # 🔹 EDITAR FÉRIAS
    with col2:
        st.markdown("### Editar Férias")

        nome_edit = st.selectbox("Colaborador", nomes, key="edit_nome")

        inicio_edit = st.date_input("Novo início", key="edit_inicio")
        fim_edit = st.date_input("Novo fim", key="edit_fim")

        if st.button("Salvar Alteração"):
            try:
                from services.pontomais import get_absences, editar_ausencia

                emp = next(c for c in colaboradores if c["Nome"] == nome_edit)

                inicio_str = inicio_edit.strftime("%d/%m/%Y")
                fim_str = fim_edit.strftime("%d/%m/%Y")

                absences = get_absences(emp["ID"])

                ausencia = encontrar_ausencia_por_periodo(
                    absences,
                    inicio_str,
                    fim_str
                )

                if not ausencia:
                    st.error("Nenhuma ausência encontrada nesse período")
                    st.stop()

                editar_ausencia(
                    employee_id=emp["ID"],
                    absence_id=ausencia["id"],
                    inicio=inicio_str,
                    fim=fim_str,
                    tipo="ferias"
                )

                st.success("Férias atualizadas com sucesso")

            except Exception as e:
                st.error(str(e))