import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import json

def append_row(sheet_name, row):
    client = get_client()
    planilha = client.open_by_key(SHEET_ID)

    sheet = planilha.worksheet(sheet_name)
    sheet.append_row(row)

def salvar_no_sheets(dados):

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    planilha = client.open_by_key("1l4tvrE8A906ctO3xJjlTQx1Lw58yewxTN83cGfZMJ6M")

    aba = planilha.worksheet("Resumo Ponto Hoje")

    aba.clear()

    if not dados:
        return

    # 🔥 HEADER PADRÃO (fixo)
    header = [
        "Nome",
        "Líder",
        "Qtd Batidas",
        "Entrada 1",
        "Saída 1",
        "Entrada 2",
        "Saída 2",
        "Horas Trabalhadas",
        "Intervalo",
        "Status Intervalo",
        "Status Dia",
        "Data"
    ]

    rows = [[
        d.get("Nome"),
        d.get("Líder"),
        d.get("Qtd Batidas"),
        d.get("Entrada 1"),
        d.get("Saída 1"),
        d.get("Entrada 2"),
        d.get("Saída 2"),
        d.get("Horas Trabalhadas"),
        d.get("Intervalo"),
        d.get("Status Intervalo"),
        d.get("Status Dia"),
        d.get("Data")
    ] for d in dados]

    aba.update("A1", [header] + rows)


    