import json

import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials


DEFAULT_SHEET_ID = "1l4tvrE8A906ctO3xJjlTQx1Lw58yewxTN83cGfZMJ6M"
SHEET_ID = st.secrets.get("GOOGLE_SHEETS_ID", DEFAULT_SHEET_ID)

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


def get_client():
    creds_raw = st.secrets["GOOGLE_CREDENTIALS"]
    creds_dict = json.loads(creds_raw) if isinstance(creds_raw, str) else creds_raw
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPES)
    return gspread.authorize(creds)


def get_spreadsheet():
    return get_client().open_by_key(SHEET_ID)


def get_data(sheet_name):
    sheet = get_spreadsheet().worksheet(sheet_name)
    return sheet.get_all_values()


def append_row(sheet_name, row):
    sheet = get_spreadsheet().worksheet(sheet_name)
    sheet.append_row(row)


def salvar_no_sheets(dados, sheet_name="Resumo Ponto Hoje"):
    sheet = get_spreadsheet().worksheet(sheet_name)
    sheet.clear()

    if not dados:
        return

    headers = list(dados[0].keys())
    rows = [[item.get(header, "") for header in headers] for item in dados]

    sheet.update("A1", [headers] + rows)
