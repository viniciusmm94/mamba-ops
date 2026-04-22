import gspread
from oauth2client.service_account import ServiceAccountCredentials

def salvar_no_sheets(dados):

    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = ServiceAccountCredentials.from_json_keyfile_name("cred.json", scope)
    client = gspread.authorize(creds)

    # 👇 TROCA PELO NOME EXATO DA SUA PLANILHA
    planilha = client.open_by_key("1l4tvrE8A906ctO3xJjlTQx1Lw58yewxTN83cGfZMJ6M")

    # 👇 NOME DA ABA
    aba = planilha.worksheet("Colaboradores")

    aba.clear()

    header = list(dados[0].keys())
    rows = [list(d.values()) for d in dados]

    aba.update("A1", [header] + rows)