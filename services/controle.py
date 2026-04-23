from datetime import datetime
from services.pontomais import get_absences
from services.sheets import get_data


# =========================
# 🔹 CONFIG
# =========================

LIMITE_PADRAO_ATRASO = "08:15"

NOMES_EXCLUIDOS = {
'Anthony Chub Generoso',
'Ariane de Queiroz Proença Fernandes',
'Arlindo Goes da Silva',
'Beatriz Pereira Macia',
'Bianca Oliveira Nôsa',
'Carolina Mendes Fonseca',
'Cristina Aparecida da Anunciação dos Santos Lima',
'Débora Cristina Soares de Oliveira',
'Gabriel Batista do Carmo Paiva',
'Gabriel Ribeiro Dos Santos',
'Gabriel Silva Soares',
'Giovana da Silva Ribeiro',
'Guilherme de Carvalho Rocha',
'Jeniffer Lima Dias da Silva',
'João Victor Gomes Dos Santos',
'Lais Gabrielle Dias',
'Laura Costa de Almeida',
'Lucas Freire Rodrigues Croce Pereira',
'Luísa Andrade Martins Moniz Teixeira',
'Matheus Honorato Daniel',
'Pedro Henrique Araujo Doconski',
'Rafael Neves Rodrigues',
'Roger Ferreira Gomes',
'Vitor Leite Rodrigues Lopes',
'Vitória Carvalho Santana',
'Wellington Dantas Moreira',
'Leonardo Roversi Coelho',
'Lygia Ferreira da Silva',
'Graziele Rocha Vasconcelos',
'Kaique Monteiro dos Santos',
'Peterson Evangelista Tourinho',
'Francielly Ferreira Motta dos Santos',
'Vinícius Vieira Cavalcante',
'Cybele Dias Dos Santos Freire',
'Caue Paiva Lucena Paiva Lucena',
'Adriano Souza de Castro',
'Beatriz Cristina Paulo Ferraz Maul Lins',
'Marco Aurelio Aragoni Pedroza',
'Kaique Monteiro dos Reis',
'Kaua Nascimento da Cruz',
'Matheus Ferreira Alves',
'Marcos Vinicius Santos Silva',
'Nathaly Pires Lima',
}

EXCECOES_ATRASO = {
    'Tamara Soares Gomes Espíndola': '09:15',
    'Andressa Cerabando Forganes Silvestre': '10:15',
    'Maria Lucilda do Nascimento': '10:15',
    'Alexandra Renata Gonçalves Barreto da Silva': '11:15'
}


# =========================
# 🔹 UTILS
# =========================

def normalizar_hora(valor):
    if not valor:
        return ""
    return str(valor).strip().replace("h", ":")


def is_excluido(nome):
    return nome.strip() in NOMES_EXCLUIDOS


# =========================
# 🔹 FÉRIAS MANUAL (SHEETS)
# =========================

def get_ferias_manual():
    rows = get_data("Ferias Manual")

    result = []

    for r in rows[1:]:
        if len(r) < 3:
            continue

        result.append({
            "nome": r[0],
            "inicio": r[1],
            "fim": r[2]
        })

    return result


def esta_em_ferias_manual(nome, data_ponto, ferias_manual):

    data_ref = datetime.strptime(data_ponto, "%d/%m/%Y")

    for f in ferias_manual:
        if nome != f["nome"]:
            continue

        try:
            inicio = datetime.strptime(f["inicio"], "%d/%m/%Y")
            fim = datetime.strptime(f["fim"], "%d/%m/%Y")
        except:
            continue

        if inicio <= data_ref <= fim:
            return True

    return False


# =========================
# 🔹 ABSENCES (API)
# =========================

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


# =========================
# 🔹 FUNÇÃO PRINCIPAL
# =========================

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

    # =========================
    # RESUMO DO DIA
    # =========================

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

    # 🔥 CACHE
    absences_cache = {}

    def get_absences_cached(emp_id):
        if emp_id in absences_cache:
            return absences_cache[emp_id]

        data = get_absences(emp_id)
        absences_cache[emp_id] = data
        return data

    # 🔥 CARREGA FÉRIAS MANUAL
    ferias_manual = get_ferias_manual()

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
    # AUSENTES + INTELIGÊNCIA
    # =========================

    for nome, lider in colaboradores_map.items():

        if is_excluido(nome):
            continue

        if nome not in quem_bateu:

            emp_id = id_map.get(nome)
            status_final = "Ausente"

            # 🔹 PRIORIDADE 1 → API
            if emp_id:
                absences = get_absences_cached(emp_id)
                status_ausencia = esta_em_ausencia(absences, data_ponto)

                if status_ausencia:
                    status_final = status_ausencia

            # 🔹 PRIORIDADE 2 → SHEETS
            if status_final == "Ausente":
                if esta_em_ferias_manual(nome, data_ponto, ferias_manual):
                    status_final = "Férias"

            resultado.append({
                "Data": data_ponto,
                "Nome": nome,
                "Líder": lider,
                "Status": status_final,
                "Horário": ""
            })

    return resultado