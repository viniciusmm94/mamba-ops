import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

LIMITE_PADRAO_ATRASO = "08:15"

NOMES_EXCLUIDOS = {
    'Anthony Chub Generoso',
    'Ariane de Queiroz Proença Fernandes',
    # ... mantém todos
}

EXCECOES_ATRASO = {
    'Tamara Soares Gomes Espíndola': '09:15',
    'Andressa Cerabando Forganes Silvestre': '10:15',
    'Maria Lucilda do Nascimento': '10:15',
    'Alexandra Renata Gonçalves Barreto da Silva': '11:15'
}


def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    import json

    creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        creds_dict,
        scope
    )

    return gspread.authorize(creds)


def normalizar_hora(valor):
    if not valor:
        return ""

    valor = str(valor).strip().replace("h", ":")
    return valor


def registrar_controle_diario():

    client = get_client()
    planilha = client.open_by_key("1l4tvrE8A906ctO3xJjlTQx1Lw58yewxTN83cGfZMJ6M")

    resumo = planilha.worksheet("Resumo Ponto Hoje")
    colaboradores = planilha.worksheet("Colaboradores")

    try:
        controle = planilha.worksheet("Controle Diário")
    except:
        controle = planilha.add_worksheet("Controle Diário", 1000, 5)
        controle.append_row(["Data", "Nome", "Líder", "Status", "Horário"])

    # =========================
    # COLABORADORES
    # =========================

    col_data = colaboradores.get_all_values()[1:]

    colaboradores_map = {}

    for r in col_data:
        nome = (r[1] or "").strip()
        lider = (r[4] or "").strip()

        if not nome or nome in NOMES_EXCLUIDOS:
            continue

        colaboradores_map[nome] = lider

    # =========================
    # RESUMO DO DIA
    # =========================

    resumo_data = resumo.get_all_values()[1:]

    quem_bateu = {}
    data_ponto = None

    for r in resumo_data:
        nome = (r[0] or "").strip()
        hora = r[3]
        data_raw = r[11] if len(r) > 11 else None

        if not data_ponto and data_raw:
            data_ponto = str(data_raw).strip()

        if not nome or not hora:
            continue

        quem_bateu[nome] = hora

    if not data_ponto:
        raise Exception("Data do ponto não encontrada")

    # =========================
    # DEDUP
    # =========================

    existentes = set()

    for r in controle.get_all_values()[1:]:
        data = str(r[0]).strip()
        nome = (r[1] or "").strip()

        if data and nome:
            existentes.add(f"{data}|{nome}")

    novas_linhas = []

    # =========================
    # ATRASADOS
    # =========================

    for nome, hora_raw in quem_bateu.items():

        if nome in NOMES_EXCLUIDOS:
            continue

        hora = normalizar_hora(hora_raw)
        limite = EXCECOES_ATRASO.get(nome, LIMITE_PADRAO_ATRASO)

        chave = f"{data_ponto}|{nome}"

        if hora > limite and chave not in existentes:
            novas_linhas.append([
                data_ponto,
                nome,
                colaboradores_map.get(nome, ""),
                "Atrasado",
                hora
            ])
            existentes.add(chave)

    # =========================
    # AUSENTES
    # =========================

    for nome, lider in colaboradores_map.items():

        chave = f"{data_ponto}|{nome}"

        if nome not in quem_bateu and chave not in existentes:
            novas_linhas.append([
                data_ponto,
                nome,
                lider,
                "Ausente",
                ""
            ])
            existentes.add(chave)

    # =========================
    # SALVAR
    # =========================

    if novas_linhas:
        controle.append_rows(novas_linhas)

    return len(novas_linhas)