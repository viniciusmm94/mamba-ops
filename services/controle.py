from datetime import datetime
from services.pontomais import get_absences


def normalizar_hora(valor):
    if not valor:
        return ""

    return str(valor).strip().replace("h", ":")


LIMITE_PADRAO_ATRASO = "08:15"

NOMES_EXCLUIDOS = {
    'Anthony Chub Generoso',
    'Ariane de Queiroz Proença Fernandes',
    # (mantém sua lista completa aqui)
}

EXCECOES_ATRASO = {
    'Tamara Soares Gomes Espíndola': '09:15',
    'Andressa Cerabando Forganes Silvestre': '10:15',
    'Maria Lucilda do Nascimento': '10:15',
    'Alexandra Renata Gonçalves Barreto da Silva': '11:15'
}


def is_excluido(nome):
    return nome.strip() in NOMES_EXCLUIDOS


# 🔥 NOVA FUNÇÃO
def esta_em_ausencia(absences, data_ponto):

    data_ref = datetime.strptime(data_ponto, "%d/%m/%Y")

    for abs in absences:
        try:
            inicio = datetime.strptime(abs["start_date"], "%d/%m/%Y")
            fim = datetime.strptime(abs["end_date"], "%d/%m/%Y")

            if inicio <= data_ref <= fim:
                return abs.get("observation", "Afastado")
        except:
            continue

    return None


def registrar_controle_diario(dados_resumo, colaboradores):

    colaboradores_map = {}
    id_map = {}

    for c in colaboradores:
        nome = (c.get("Nome") or "").strip()
        lider = (c.get("Equipe") or "").strip()
        emp_id = c.get("ID")

        if not nome or is_excluido(nome):
            continue

        colaboradores_map[nome] = lider
        id_map[nome] = emp_id

    quem_bateu = {}
    data_ponto = None

    for d in dados_resumo:
        nome = (d.get("Nome") or "").strip()
        hora = d.get("Entrada 1")
        data_raw = d.get("Data")

        if not data_ponto and data_raw:
            data_ponto = data_raw

        if not nome or not hora:
            continue

        if is_excluido(nome):
            continue

        quem_bateu[nome] = hora

    if not data_ponto:
        raise Exception("Data do ponto não encontrada")

    resultado = []

    # 🔥 CACHE (evita múltiplas chamadas)
    absences_cache = {}

    def get_absences_cached(emp_id):
        if emp_id in absences_cache:
            return absences_cache[emp_id]

        data = get_absences(emp_id)
        absences_cache[emp_id] = data
        return data

    # =========================
    # ATRASADOS
    # =========================

    for nome, hora_raw in quem_bateu.items():

        if is_excluido(nome):
            continue

        hora = normalizar_hora(hora_raw)
        limite = EXCECOES_ATRASO.get(nome, LIMITE_PADRAO_ATRASO)

        if hora > limite:
            resultado.append({
                "Data": data_ponto,
                "Nome": nome,
                "Líder": colaboradores_map.get(nome, ""),
                "Status": "Atrasado",
                "Horário": hora
            })

    # =========================
    # AUSENTES + ABSENCES
    # =========================

    for nome, lider in colaboradores_map.items():

        if is_excluido(nome):
            continue

        if nome not in quem_bateu:

            emp_id = id_map.get(nome)
            status_final = "Ausente"

            if emp_id:
                absences = get_absences_cached(emp_id)
                status_ausencia = esta_em_ausencia(absences, data_ponto)

                if status_ausencia:
                    status_final = status_ausencia

            resultado.append({
                "Data": data_ponto,
                "Nome": nome,
                "Líder": lider,
                "Status": status_final,
                "Horário": ""
            })

    return resultado