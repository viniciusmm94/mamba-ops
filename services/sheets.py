import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import json

def salvar_no_sheets(dados):

    print(">>> EXECUTANDO SALVAR NO SHEETS")

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # 👇 PEGA STRING DO SECRETS
    creds_json = st.secrets["GOOGLE_CREDENTIALS"]

    # 👇 AJUSTA QUEBRA DE LINHA DO PRIVATE KEY
    creds_dict = json.loads(creds_json.replace("\n", "\\n"))

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    planilha = client.open_by_key("1l4tvrE8A906ctO3xJjlTQx1Lw58yewxTN83cGfZMJ6M")

    aba = planilha.sheet1

    aba.clear()

    header = list(dados[0].keys())
    rows = [list(d.values()) for d in dados]

    aba.update("A1", [header] + rows)