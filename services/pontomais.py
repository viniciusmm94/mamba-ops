import requests
import time
import streamlit as st

BASE_URL = "https://api.pontomais.com.br/external_api/v1"


def listar_colaboradores_ativos():
    TOKEN = st.secrets["PONTOMAIS_TOKEN"]

    linhas = []
    page = 1
    per_page = 100

    while True:
        url = (
            f"{BASE_URL}/employees"
            f"?page={page}"
            f"&per_page={per_page}"
            f"&status=active"
            f"&attributes=id,name,email,cpf,team,job_title,admission_date"
        )

        retry = 0

        while retry < 3:
            response = requests.get(
                url,
                headers={
                    "access-token": TOKEN,
                    "Content-Type": "application/json"
                }
            )

            if response.status_code == 429:
                time.sleep(5)
                retry += 1
                continue

            if response.status_code != 200:
                raise Exception(f"Erro API página {page}: {response.text}")

            break

        data = response.json()
        employees = data.get("employees", [])

        if not employees:
            break

        for emp in employees:
            linhas.append({
                "ID": emp.get("id"),
                "Nome": emp.get("name"),
                "Email": emp.get("email"),
                "CPF": emp.get("cpf"),
                "Equipe": (emp.get("team") or {}).get("name"),
                "Cargo": (emp.get("job_title") or {}).get("name"),
                "Data Admissão": emp.get("admission_date"),
            })

        if len(employees) < per_page:
            break

        page += 1
        time.sleep(0.5)

    return linhas


def resumo_ponto_por_data(data_br):
    TOKEN = st.secrets["PONTOMAIS_TOKEN"]

    d, m, y = data_br.split("/")
    data_iso = f"{y}-{m}-{d}"

    payload = {
        "report": {
            "start_date": data_iso,
            "end_date": data_iso,
            "columns": "employee_name,team_name,date,time",
            "format": "csv"
        }
    }

    response = requests.post(
        f"{BASE_URL}/reports/time_cards",
        json=payload,
        headers={
            "access-token": TOKEN,
            "Content-Type": "application/json"
        }
    )

    if response.status_code != 200:
        raise Exception(response.text)

    import csv
    from io import StringIO
    from collections import defaultdict

    csv_data = list(csv.reader(StringIO(response.text)))
    by_employee = defaultdict(list)

    for i, row in enumerate(csv_data):
        if i == 0:
            continue

        # 🔥 evita quebra
        if len(row) < 4:
            continue

        nome = row[0].strip()
        lider = row[1].strip()
        hora = row[3].strip()

        if not nome or not hora:
            continue

        by_employee[(nome, lider)].append(hora)

    def to_min(h):
        h, m = map(int, h.split(":"))
        return h * 60 + m

    def to_hhmm(m):
        if m <= 0:
            return "00:00"
        return f"{m//60:02}:{m%60:02}"

    output = []

    for (nome, lider), times in by_employee.items():
        times.sort()

        qtd = len(times)
        e1, s1, e2, s2 = (times + ["", "", "", ""])[:4]

        status_dia = "OK"
        status_intervalo = "OK"
        horas = ""
        intervalo = ""

        if qtd == 1 or qtd > 4:
            status_dia = "Inconsistente"

        tE1 = to_min(e1) if e1 else None
        tS1 = to_min(s1) if s1 else None
        tE2 = to_min(e2) if e2 else None
        tS2 = to_min(s2) if s2 else None

        if qtd == 2 and tE1 and tS1:
            horas = to_hhmm(tS1 - tE1)

        if qtd == 3 and tE1 and tE2:
            horas = to_hhmm(tE2 - tE1)

        if qtd >= 4 and tE1 and tS1 and tE2 and tS2:
            horas = to_hhmm((tS1 - tE1) + (tS2 - tE2))

        if tS1 and tE2:
            inter = tE2 - tS1
            intervalo = to_hhmm(inter)
            if inter < 60:
                status_intervalo = "Intervalo Irregular"

        output.append({
            "Nome": nome,
            "Líder": lider,
            "Qtd Batidas": qtd,
            "Entrada 1": e1,
            "Saída 1": s1,
            "Entrada 2": e2,
            "Saída 2": s2,
            "Horas Trabalhadas": horas,
            "Intervalo": intervalo,
            "Status Intervalo": status_intervalo,
            "Status Dia": status_dia,
            "Data": data_br
        })

    return output