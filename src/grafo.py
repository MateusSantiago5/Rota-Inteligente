from pathlib import Path
import pandas as pd
import networkx as nx


def carregar_grafo(pasta_data: Path):
    """Carrega os pontos e as ruas e monta um grafo simples."""
    pontos = pd.read_csv(pasta_data / "pontos.csv")
    arestas = pd.read_csv(pasta_data / "arestas.csv")

    grafo = nx.Graph()

    for _, linha in pontos.iterrows():
        grafo.add_node(
            linha["no"],
            nome=linha["nome"],
            x=float(linha["x"]),
            y=float(linha["y"]),
            tipo=linha["tipo"],
        )

    for _, linha in arestas.iterrows():
        grafo.add_edge(
            linha["origem"],
            linha["destino"],
            weight=float(linha["distancia_km"]),
        )

    return grafo, pontos, arestas


def heuristica(grafo, no_atual, destino):
    """Distancia em linha reta usada pelo A*."""
    x1, y1 = grafo.nodes[no_atual]["x"], grafo.nodes[no_atual]["y"]
    x2, y2 = grafo.nodes[destino]["x"], grafo.nodes[destino]["y"]
    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def caminho_astar(grafo, origem, destino):
    caminho = nx.astar_path(
        grafo,
        origem,
        destino,
        heuristic=lambda a, b: heuristica(grafo, a, b),
        weight="weight",
    )
    distancia = nx.path_weight(grafo, caminho, weight="weight")
    return caminho, distancia


def distancia_do_caminho(grafo, caminho):
    if not caminho or len(caminho) == 1:
        return 0.0
    return nx.path_weight(grafo, caminho, weight="weight")
