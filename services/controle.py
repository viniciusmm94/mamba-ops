from services.pontomais import get_status_colaborador

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

STATUS_MAP = {
    9: "Afastado",
    11: "Férias"
}


def normalizar_hora(valor):
    if not valor:
        return ""
    return str(valor).strip().replace("h", ":")


def is_excluido(nome):
    return nome.strip().lower() in {n.lower() for n in NOMES_EXCLUIDOS}


def registrar_controle_diario(dados_resumo, colaboradores):

    colaboradores_map = {}
    id_map = {}

    for c in colaboradores:
        nome = (c.get("Nome") or "").strip()

        if not nome or is_excluido(nome):
            continue

        colaboradores_map[nome] = c.get("Equipe")
        id_map[nome] = c.get("ID")

    quem_bateu = {}
    data_ponto = None

    for d in dados_resumo:
        nome = (d.get("Nome") or "").strip()

        if is_excluido(nome):
            continue

        hora = d.get("Entrada 1")
        data_raw = d.get("Data")

        if not data_ponto and data_raw:
            data_ponto = data_raw

        if nome and hora:
            quem_bateu[nome] = hora

    if not data_ponto:
        raise Exception("Data do ponto não encontrada")

    resultado = []
    status_cache = {}

    def get_status_cached(emp_id):
        if emp_id in status_cache:
            return status_cache[emp_id]

        status = get_status_colaborador(emp_id)
        status_cache[emp_id] = status
        return status

    # ATRASADOS
    for nome, hora_raw in quem_bateu.items():

        hora = normalizar_hora(hora_raw)
        limite = EXCECOES_ATRASO.get(nome, LIMITE_PADRAO_ATRASO)

        if hora > limite:
            resultado.append({
                "Data": data_ponto,
                "Nome": nome,
                "Líder": colaboradores_map.get(nome),
                "Status": "Atrasado",
                "Horário": hora
            })

    # AUSENTES + STATUS REAL
    for nome, lider in colaboradores_map.items():

        if nome not in quem_bateu:

            emp_id = id_map.get(nome)
            status_api = get_status_cached(emp_id) if emp_id else None

            status_final = STATUS_MAP.get(status_api, "Ausente")

            resultado.append({
                "Data": data_ponto,
                "Nome": nome,
                "Líder": lider,
                "Status": status_final,
                "Horário": ""
            })

    return resultado