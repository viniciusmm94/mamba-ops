import requests
import time
import streamlit as st

BASE_URL = "https://api.pontomais.com.br/external_api/v1"


@st.cache_data(ttl=300)
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