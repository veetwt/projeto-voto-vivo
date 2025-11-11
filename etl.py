import requests
import sqlite3
import time

def extrair_todos_deputados():
    base_url = "https://dadosabertos.camara.leg.br/api/v2/deputados"
    filtro = {'itens': 100, 'pagina': 1, 'ordem': 'ASC', 'ordenarPor': 'nome'} #limitação definifinida na doc da api

    todos_deputados = []

    while True:
        response = requests.get(base_url, params=filtro)
        if response.status_code != 200:
            print(f"Erro ao buscar página {filtro['pagina']}.")
            break

        dados = response.json()
        todos_deputados.extend(dados['dados'])

        link_next = next((link['href'] for link in dados['links'] if link['rel'] == 'next'), None)
        if not link_next:
            break 

        filtro['pagina'] += 1
        time.sleep(1) 

    print(f"total de deputados: {len(todos_deputados)}")
    return todos_deputados

def extrair_despesas_deputado(id_deputado):
    base_url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{id_deputado}/despesas"
    filtros = {'itens': 100, 'pagina': 1, 'ordenarPor': 'ano'}

    todas_despesas = []

    while True:
        response = requests.get(base_url, params=filtros)
        if response.status_code != 200:
            break 

        dados = response.json()
        todas_despesas.extend(dados['dados'])

        link_next = next((link['href'] for link in dados['links'] if link['rel'] == 'next'), None)
        if not link_next:
            break

        filtros['pagina'] += 1
        time.sleep(0.5) 

    print(f"total de despesas: {len(todas_despesas)}")
    return todas_despesas

def carregar_deputados_no_banco(deputados, conn):
    cursor = conn.cursor()

    for dep in deputados:
        dados_mapeados = (
            dep['id'],
            dep['nome'],
            dep['siglaPartido'],
            dep['siglaUf'],
            dep['urlFoto']
        )

        cursor.execute("""
        INSERT OR IGNORE INTO Deputados (id, nome, partido, sigla_uf, url_foto) 
        VALUES (?, ?, ?, ?, ?)
        """, dados_mapeados)

    conn.commit()
    print("deputados inseridos no banco")

def carregar_despesas_no_banco(id_deputado, despesas, conn):
    cursor = conn.cursor()

    for despesa in despesas:
        dados_mapeados = (
            id_deputado,
            despesa['ano'],
            despesa['mes'],
            despesa['tipoDespesa'],
            despesa['valorLiquido']
        )

        cursor.execute("""
        INSERT INTO Despesas (id_deputado, ano, mes, tipo_despesa, valor_liquido)
        VALUES (?, ?, ?, ?, ?)
        """, dados_mapeados)

    conn.commit()
    print("despesas inseridas no banco")

def main():
    conn = sqlite3.connect('voto_vivo.db')

    lista_deputados_api = extrair_todos_deputados()

    if lista_deputados_api:
        carregar_deputados_no_banco(lista_deputados_api, conn)

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Deputados")
    ids_deputados_no_banco = [row[0] for row in cursor.fetchall()]

    cursor.execute("DELETE FROM Despesas") #vai carregar tudo de novo
    conn.commit()

    for id_dep in ids_deputados_no_banco:
        lista_despesas_api = extrair_despesas_deputado(id_dep)

        if lista_despesas_api:
            carregar_despesas_no_banco(id_dep, lista_despesas_api, conn)

    conn.close()
    print("\netl concluido")

if __name__ == "__main__":
    main()