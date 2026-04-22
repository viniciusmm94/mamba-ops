# ==============================
# 🔹 BLOCO 3 — CONTROLE DIÁRIO
# ==============================

st.subheader("Controle Diário")

if st.button("Gerar Controle"):

    with st.spinner("Processando controle..."):
        try:
            colaboradores = listar_colaboradores_ativos()
            dados = resumo_ponto_por_data(data)

            resultado = registrar_controle_diario(dados, colaboradores)

            df = pd.DataFrame(resultado)

            st.success(f"{len(df)} registros encontrados")
            st.dataframe(df, width="stretch")

        except Exception as e:
            st.error(str(e))