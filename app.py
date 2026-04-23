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

    # 🔥 CACHE (performance)
    @st.cache_data
    def get_colaboradores():
        return listar_colaboradores_ativos()

    colaboradores = get_colaboradores()
    nomes = [c["Nome"] for c in colaboradores]

    nome_sel = st.selectbox("Selecionar colaborador", nomes)

    emp = next(c for c in colaboradores if c["Nome"] == nome_sel)

    # ==============================
    # 🔹 VISUALIZAR FÉRIAS ATUAIS
    # ==============================

    st.markdown("### Férias atuais")

    with st.spinner("Carregando dados..."):
        absences = get_absences(emp["ID"])

    if absences:
        df_abs = pd.DataFrame(absences)
        st.dataframe(df_abs, use_container_width=True)
    else:
        st.info("Nenhuma ausência encontrada")

    st.divider()

    col1, col2 = st.columns(2)

    # ==============================
    # 🔹 FORM — CADASTRAR
    # ==============================

    with col1:
        st.markdown("### Cadastrar Férias")

        with st.form("form_create"):
            inicio = st.date_input("Data início", key="create_inicio")
            fim = st.date_input("Data fim", key="create_fim")

            submit_create = st.form_submit_button("Cadastrar")

            if submit_create:
                try:
                    # 🔥 validação
                    if inicio > fim:
                        st.warning("Data de início maior que fim")
                        st.stop()

                    with st.spinner("Cadastrando férias..."):
                        criar_ferias(
                            employee_id=emp["ID"],
                            inicio=inicio.strftime("%d/%m/%Y"),
                            fim=fim.strftime("%d/%m/%Y")
                        )

                    st.success(
                        f"Férias cadastradas para {nome_sel} de "
                        f"{inicio.strftime('%d/%m')} até {fim.strftime('%d/%m')}"
                    )

                    st.rerun()

                except Exception as e:
                    st.error("Erro ao cadastrar férias")


    # ==============================
    # 🔹 FORM — EDITAR
    # ==============================

    with col2:
        st.markdown("### Editar Férias")

        with st.form("form_edit"):
            inicio_edit = st.date_input("Novo início", key="edit_inicio")
            fim_edit = st.date_input("Novo fim", key="edit_fim")

            submit_edit = st.form_submit_button("Salvar Alteração")

            if submit_edit:
                try:
                    if inicio_edit > fim_edit:
                        st.warning("Data de início maior que fim")
                        st.stop()

                    inicio_str = inicio_edit.strftime("%d/%m/%Y")
                    fim_str = fim_edit.strftime("%d/%m/%Y")

                    ausencia = encontrar_ausencia_por_periodo(
                        absences,
                        inicio_str,
                        fim_str
                    )

                    if not ausencia:
                        st.error("Nenhuma ausência encontrada nesse período")
                        st.stop()

                    with st.spinner("Atualizando férias..."):
                        editar_ausencia(
                            employee_id=emp["ID"],
                            absence_id=ausencia["id"],
                            inicio=inicio_str,
                            fim=fim_str,
                            tipo="ferias"
                        )

                    st.success(
                        f"Férias atualizadas para {nome_sel} "
                        f"({inicio_str} → {fim_str})"
                    )

                    st.rerun()

                except Exception as e:
                    st.error("Erro ao editar férias")