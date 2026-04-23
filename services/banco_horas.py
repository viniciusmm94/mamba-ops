import requests
from datetime import datetime, timedelta
import math

BASE_URL = "https://api.pontomais.com.br/external_api/v1/reports/time_balances"

def format_iso(date):
    return date.strftime("%Y-%m-%d")


def to_minutes(hora):
    if not hora:
        return 0

    s = str(hora).strip()
    sign = -1 if s.startswith('-') else 1
    s = s.replace('+', '').replace('-', '')

    h, m = map(int, s.split(':'))
    return sign * (h * 60 + m)


def from_minutes(mins):
    h = abs(mins) // 60
    m = abs(mins) % 60
    return f"{h:02}:{m:02}"


def diff_horas(a, b):
    diff = to_minutes(a) - to_minutes(b)
    sign = '+' if diff > 0 else '-' if diff < 0 else ''
    return sign + from_minutes(diff)


def gerar_banco_horas(token):
    hoje = datetime.now()
    inicio_mes = hoje.replace(day=1)
    ontem = hoje - timedelta(days=1)

    # semanas
    semanas = sorted(list({
        math.ceil((inicio_mes + timedelta(days=i)).day / 7)
        for i in range((ontem - inicio_mes).days + 1)
    }))

    payload = {
        "report": {
            "start_date": format_iso(inicio_mes),
            "end_date": format_iso(ontem),
            "group_by": "team",
            "columns": "name,team_name,date,time_balance",
            "format": "json"
        }
    }

    response = requests.post(
        BASE_URL,
        json=payload,
        headers={"access-token": token}
    )

    data = response.json()
    rows = []

    for g in data["data"][0]:
        rows.extend(g["data"])

    saldos = {}

    for r in rows:
        nome = r["name"]
        equipe = r.get("team_name", "")
        data_obj = datetime.strptime(r["date"].split(", ")[1], "%d/%m/%Y")
        semana = math.ceil(data_obj.day / 7)

        if nome not in saldos:
            saldos[nome] = {"team": equipe, "semanas": {}}

        saldos[nome]["semanas"][semana] = r.get("time_balance", "00:00")

    output = []

    for nome, info in sorted(saldos.items()):
        linha = {
            "Nome": nome,
            "Equipe": info["team"]
        }

        valores = []

        for s in semanas:
            val = info["semanas"].get(s, "00:00")
            linha[f"Semana {s}"] = val
            valores.append(val)

        acumulado = valores[-1] if valores else "00:00"
        anterior = valores[-2] if len(valores) > 1 else "00:00"

        linha["Acumulado"] = acumulado
        linha["Comparação"] = diff_horas(acumulado, anterior)

        output.append(linha)

    return output