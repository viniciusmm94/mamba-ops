def normalizar_hora(valor):
    if not valor:
        return ""

    return str(valor).strip().replace("h", ":")


LIMITE_PADRAO_ATRASO = "08:15"

NOMES_EXCLUIDOS = {
    'Anthony Chub Generoso',
    'Ariane de Queiroz Proença Fernandes',
}

EXCECOES_ATRASO = {
    'Tamara Soares Gomes Espíndola': '09:15',
    'Andressa Cerabando Forganes Silvestre': '10:15',
    'Maria Lucilda do Nascimento': '10:15',
    'Alexandra Renata Gonçalves Barreto da Silva': '11:15'
}


def registrar_controle_diario(dados_resumo, colaboradores):

    # =========================
    # MAPA DE COLABORADORES
    # =========================

    colaboradores_map = {}

    for c in colaboradores:
        nome = (c.get("Nome") or "").strip()
        lider = (c.get("Equipe") or "").strip()

        if not nome or nome in NOMES_EXCLUIDOS:
            continue

        colaboradores_map[nome] = lider

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

        quem_bateu[nome] = hora

    if not data_ponto:
        raise Exception("Data do ponto não encontrada")

    resultado = []

    # =========================
    # ATRASADOS
    # =========================

    for nome, hora_raw in quem_bateu.items():

        if nome in NOMES_EXCLUIDOS:
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
    # AUSENTES
    # =========================

    for nome, lider in colaboradores_map.items():

        if nome not in quem_bateu:
            resultado.append({
                "Data": data_ponto,
                "Nome": nome,
                "Líder": lider,
                "Status": "Ausente",
                "Horário": ""
            })

    return resultado