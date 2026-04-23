import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos, resumo_ponto_por_data
from services.sheets import salvar_no_sheets
from services.controle import registrar_controle_diario, encontrar_ausencia_por_periodo

st.set_page_config(layout="wide")
st.title("Mamba Ops")

# ==============================
# 🔹 BLOCO 1 — COLABORADORES
# ==============================

st.subheader("Colaboradores")

if st.button("Atualizar Colaboradores"):
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
    try:
        colaboradores = listar_colaboradores_ativos()
        dados = resumo_ponto_por_data(data)

        resultado = registrar_controle_diario(dados, colaboradores)
        df = pd.DataFrame(resultado)

        st.success(f"{len(df)} registros encontrados")
        st.dataframe(df, width="stretch")

    except Exception as e:
        st.error(str(e))


# ==============================
# 🔹 BLOCO 4 — FÉRIAS MANUAL (SHEETS)
# ==============================

st.subheader("Cadastrar Férias Manual")

nome = st.text_input("Nome completo")
inicio_manual = st.date_input("Data início", key="manual_inicio")
fim_manual = st.date_input("Data fim", key="manual_fim")

if st.button("Salvar Férias Manual"):
    try:
        from services.sheets import append_row

        append_row("Ferias Manual", [
            nome,
            inicio_manual.strftime("%d/%m/%Y"),
            fim_manual.strftime("%d/%m/%Y")
        ])

        st.success("Férias cadastradas")

    except Exception as e:
        st.error(str(e))


# ==============================
# 🔹 BLOCO 5 — LANÇAR FÉRIAS (API)
# ==============================

st.subheader("Lançar Férias")

colaboradores = listar_colaboradores_ativos()
nomes = [c["Nome"] for c in colaboradores]

nome_selecionado = st.selectbox("Selecionar colaborador", nomes, key="create_nome")

inicio_api = st.date_input("Data início férias", key="api_inicio")
fim_api = st.date_input("Data fim férias", key="api_fim")

if st.button("Cadastrar Férias API"):
    try:
        from services.pontomais import criar_ferias

        emp = next(c for c in colaboradores if c["Nome"] == nome_selecionado)

        criar_ferias(
            employee_id=emp["ID"],
            inicio=inicio_api.strftime("%d/%m/%Y"),
            fim=fim_api.strftime("%d/%m/%Y")
        )

        st.success("Férias cadastradas com sucesso")

    except Exception as e:
        st.error(str(e))


# ==============================
# 🔹 BLOCO 6 — EDITAR FÉRIAS
# ==============================

st.subheader("Editar Férias")

nome_sel = st.selectbox("Selecionar colaborador", nomes, key="edit_nome")

inicio_edit = st.date_input("Novo início", key="edit_inicio")
fim_edit = st.date_input("Novo fim", key="edit_fim")

if st.button("Salvar Alteração"):
    try:
        from services.pontomais import get_absences, editar_ausencia

        emp = next(c for c in colaboradores if c["Nome"] == nome_sel)

        inicio_str = inicio_edit.strftime("%d/%m/%Y")
        fim_str = fim_edit.strftime("%d/%m/%Y")

        absences = get_absences(emp["ID"])

        ausencia = encontrar_ausencia_por_periodo(absences, inicio_str, fim_str)

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