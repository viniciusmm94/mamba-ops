import gspread
import streamlit as st
import json
from google.oauth2.service_account import Credentials


def salvar_no_sheets(dados):

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

    credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)

    client = gspread.authorize(credentials)

    planilha = client.open_by_key("1l4tvrE8A906ctO3xJjlTQx1Lw58yewxTN83cGfZMJ6M")
    aba = planilha.worksheet("Colaboradores")

    aba.append_rows(rows)

    if not dados:
        return

    header = list(dados[0].keys())
    rows = [list(d.values()) for d in dados]

    aba.update("A1", [header] + rows)