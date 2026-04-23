import requests
import time
import streamlit as st

BASE_URL = "https://api.pontomais.com.br/external_api/v1"
TOKEN = st.secrets["PONTOMAIS_TOKEN"]


def listar_colaboradores_ativos():
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

        response = requests.get(
            url,
            headers={
                "access-token": TOKEN,
                "Content-Type": "application/json"
            }
        )

        if response.status_code != 200:
            raise Exception(response.text)

        data = response.json()
        employees = data.get("employees", [])

        if not employees:
            break

        for emp in employees:
            linhas.append({
                "ID": emp.get("id"),
                "Nome": emp.get("name"),
                "Equipe": (emp.get("team") or {}).get("name"),
            })

        if len(employees) < per_page:
            break

        page += 1
        time.sleep(0.5)

    return linhas


def resumo_ponto_por_data(data_br):
    import csv
    from io import StringIO
    from collections import defaultdict

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

    csv_data = list(csv.reader(StringIO(response.text)))
    by_employee = defaultdict(list)

    for i, row in enumerate(csv_data):
        if i == 0:
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
        return f"{m//60:02}:{m%60:02}" if m > 0 else "00:00"

    output = []

    for (nome, lider), times in by_employee.items():
        times.sort()

        qtd = len(times)
        e1, s1, e2, s2 = (times + ["", "", "", ""])[:4]

        output.append({
            "Nome": nome,
            "Líder": lider,
            "Entrada 1": e1,
            "Data": data_br
        })

    return output


# 🔥 STATUS API
def get_status_colaborador(employee_id):
    url = f"{BASE_URL}/employees/{employee_id}/status"

    response = requests.get(
        url,
        headers={
            "access-token": TOKEN,
            "Content-Type": "application/json"
        }
    )

    if response.status_code != 200:
        return None

    return response.json().get("status")