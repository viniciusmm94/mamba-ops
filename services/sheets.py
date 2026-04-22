import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st


def salvar_no_sheets(dados):

    # 🔥 DEBUG (pode remover depois)
    st.write(">>> salvando no sheets")

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # 🔥 IMPORTANTE: NÃO usar json.loads nem dict()
    import json

    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    planilha = client.open_by_key("1l4tvrE8A906ctO3xJjlTQx1Lw58yewxTN83cGfZMJ6M")

    aba = planilha.sheet1

    aba.clear()

    if not dados:
        st.write(">>> dados vazio")
        return

    # 🔥 garante estrutura
    dados = [d for d in dados if isinstance(d, dict)]

    if not dados:
        st.write(">>> dados inválido")
        return

    header = list(dados[0].keys())
    rows = [list(d.values()) for d in dados]

    st.write(">>> linhas:", len(rows))

    aba.update("A1", [header] + rows)