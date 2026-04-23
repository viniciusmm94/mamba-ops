import streamlit as st
import pandas as pd

from services.pontomais import listar_colaboradores_ativos, resumo_ponto_por_data
from services.sheets import salvar_no_sheets
from services.controle import registrar_controle_diario, encontrar_ausencia_por_periodo

st.set_page_config(layout="wide")
# 🔥 importa a fonte Poppins
st.markdown(
    """
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@500;600;700&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True
)

# 🔥 título customizado
st.markdown(
    """
    <h1 style="
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        font-size: 40px;
        color: #ffffff;
        margin-bottom: 0;
    ">
        Gestão de Jornada
    </h1>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="margin-top:-28px; color: #9ca3af; font-size:14px;">
        Controle diário de ponto, ausências e férias
    </div>
    """,
    unsafe_allow_html=True
)

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

    # 🔹 SELECT
    nome_sel = st.selectbox("Selecionar colaborador", nomes)
    emp = next(c for c in colaboradores if c["Nome"] == nome_sel)

    # ==============================
    # 🔹 VISUALIZAR FÉRIAS
    # ==============================

    st.markdown("### Férias atuais")

    # 🔥 SOMENTE LOADING
    with st.spinner("Carregando dados..."):
        absences = get_absences(emp["ID"])

    # 🔥 UI FORA DO SPINNER
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

        # 🔹 tabela mais alinhada (sem ocupar tudo)
        st.dataframe(df_abs)

    else:
        # 🔹 box compacto
        st.markdown(
            """
            <div style="
                max-width: 400px;
                margin: 4px 0;
                background-color: rgb(197, 180, 96);
                border: 1px solid rgba(0,0,0,0.1);
                padding: 4px 12px;
                border-radius: 4px;
                color: #333;
                font-size: 11px;
            ">
                Nenhum registro encontrado
            </div>
            """,
            unsafe_allow_html=True
        )

    # ==============================
    # 🔹 FORMULÁRIOS
    # ==============================

    st.divider()

    col1, col2 = st.columns(2)

    # 🔹 CADASTRAR
    with col1:
        st.markdown("### Cadastrar Férias")

        with st.form("form_create"):
            inicio = st.date_input("Data início", key="create_inicio")
            fim = st.date_input("Data fim", key="create_fim")

            if st.form_submit_button("Cadastrar"):
                try:
                    if inicio > fim:
                        st.warning("Data inválida")
                        st.stop()

                    with st.spinner("Cadastrando..."):
                        criar_ferias(
                            emp["ID"],
                            inicio.strftime("%d/%m/%Y"),
                            fim.strftime("%d/%m/%Y")
                        )

                    st.success("Férias cadastradas")
                    st.rerun()

                except:
                    st.error("Erro ao cadastrar")

    # 🔹 EDITAR
    with col2:
        st.markdown("### Editar Férias")

        with st.form("form_edit"):
            inicio_edit = st.date_input("Novo início", key="edit_inicio")
            fim_edit = st.date_input("Novo fim", key="edit_fim")

            if st.form_submit_button("Salvar"):
                try:
                    if inicio_edit > fim_edit:
                        st.warning("Data inválida")
                        st.stop()

                    inicio_str = inicio_edit.strftime("%d/%m/%Y")
                    fim_str = fim_edit.strftime("%d/%m/%Y")

                    ausencia = encontrar_ausencia_por_periodo(
                        absences,
                        inicio_str,
                        fim_str
                    )

                    if not ausencia:
                        st.error("Não encontrada")
                        st.stop()

                    with st.spinner("Atualizando..."):
                        editar_ausencia(
                            emp["ID"],
                            ausencia["id"],
                            inicio_str,
                            fim_str,
                            "ferias"
                        )

                    st.success("Atualizado")
                    st.rerun()

                except:
                    st.error("Erro ao editar")