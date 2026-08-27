from pathlib import Path
import sys

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

PASTA_PROJETO = Path(__file__).resolve().parents[1]
PASTA_DATA = PASTA_PROJETO / "data"
PASTA_DOCS = PASTA_PROJETO / "docs"
PASTA_OUTPUTS = PASTA_PROJETO / "outputs"

sys.path.insert(0, str(Path(__file__).resolve().parent))

from grafo import carregar_grafo, caminho_astar, distancia_do_caminho
from agrupamento import agrupar_entregas
from rotas import montar_rota_grupo


def salvar_grafo(grafo):
    pos = {no: (grafo.nodes[no]["x"], grafo.nodes[no]["y"]) for no in grafo.nodes}

    plt.figure(figsize=(10, 7))
    nx.draw_networkx(
        grafo,
        pos,
        with_labels=True,
        node_size=900,
        font_size=9,
        width=1.5,
    )
    labels = nx.get_edge_attributes(grafo, "weight")
    nx.draw_networkx_edge_labels(grafo, pos, edge_labels=labels, font_size=7)
    plt.title("Grafo simplificado da regiao atendida pela Sabor Express")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(PASTA_DOCS / "grafo_cidade.png", dpi=160, bbox_inches="tight")
    plt.close()


def salvar_mapa_rotas(grafo, entregas_grupos, rotas):
    pos = {no: (grafo.nodes[no]["x"], grafo.nodes[no]["y"]) for no in grafo.nodes}

    plt.figure(figsize=(10, 7))
    nx.draw_networkx_edges(grafo, pos, width=1.0, alpha=0.35)
    nx.draw_networkx_nodes(grafo, pos, node_size=650, alpha=0.8)
    nx.draw_networkx_labels(grafo, pos, font_size=8)

    estilos = ["solid", "dashed", "dotted"]
    for indice, grupo in enumerate(sorted(rotas)):
        rota = rotas[grupo]["rota"]
        pares = list(zip(rota[:-1], rota[1:]))
        nx.draw_networkx_edges(
            grafo,
            pos,
            edgelist=pares,
            width=3.0,
            style=estilos[indice % len(estilos)],
            alpha=0.9,
            label=f"Zona {grupo}",
        )

    plt.title("Rotas sugeridas apos agrupamento das entregas")
    plt.legend()
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(PASTA_OUTPUTS / "rotas_por_zona.png", dpi=160, bbox_inches="tight")
    plt.close()


def comparar_buscas(grafo, origem="CD", destino="K"):
    linhas = []

    caminho_a, dist_a = caminho_astar(grafo, origem, destino)
    linhas.append({
        "algoritmo": "A*",
        "caminho": " -> ".join(caminho_a),
        "quantidade_de_nos": len(caminho_a),
        "distancia_km": round(dist_a, 2),
        "observacao": "Considera a distancia das ruas e uma estimativa ate o destino.",
    })

    caminho_bfs = nx.shortest_path(grafo, origem, destino)
    linhas.append({
        "algoritmo": "BFS",
        "caminho": " -> ".join(caminho_bfs),
        "quantidade_de_nos": len(caminho_bfs),
        "distancia_km": round(distancia_do_caminho(grafo, caminho_bfs), 2),
        "observacao": "Procura pelo menor numero de passos, mas nao prioriza os pesos das ruas.",
    })

    caminho_dfs = nx.dfs_tree(grafo, source=origem)
    caminho_dfs = nx.shortest_path(caminho_dfs, origem, destino)
    linhas.append({
        "algoritmo": "DFS",
        "caminho": " -> ".join(caminho_dfs),
        "quantidade_de_nos": len(caminho_dfs),
        "distancia_km": round(distancia_do_caminho(grafo, caminho_dfs), 2),
        "observacao": "Explora um caminho em profundidade e pode percorrer uma rota maior.",
    })

    return pd.DataFrame(linhas)


def main():
    PASTA_DOCS.mkdir(exist_ok=True)
    PASTA_OUTPUTS.mkdir(exist_ok=True)

    grafo, pontos, _ = carregar_grafo(PASTA_DATA)
    entregas = pd.read_csv(PASTA_DATA / "entregas.csv")

    entregas_grupos, _ = agrupar_entregas(entregas, pontos, n_grupos=3)
    entregas_grupos.to_csv(PASTA_OUTPUTS / "entregas_com_zonas.csv", index=False)

    rotas = {}
    linhas_resultado = []

    for grupo in sorted(entregas_grupos["grupo"].unique()):
        destinos = entregas_grupos.loc[entregas_grupos["grupo"] == grupo, "no"].tolist()
        rota, ordem_entregas, distancia = montar_rota_grupo(grafo, "CD", destinos)
        rotas[int(grupo)] = {
            "rota": rota,
            "ordem_entregas": ordem_entregas,
            "distancia": distancia,
        }
        linhas_resultado.append({
            "zona": int(grupo),
            "entregas": ", ".join(ordem_entregas),
            "rota_completa": " -> ".join(rota),
            "distancia_km": round(distancia, 2),
        })

    df_rotas = pd.DataFrame(linhas_resultado)
    df_rotas.to_csv(PASTA_OUTPUTS / "resumo_rotas.csv", index=False)

    comparacao = comparar_buscas(grafo)
    comparacao.to_csv(PASTA_OUTPUTS / "comparacao_buscas.csv", index=False)

    salvar_grafo(grafo)
    salvar_mapa_rotas(grafo, entregas_grupos, rotas)

    distancia_total = df_rotas["distancia_km"].sum()

    with open(PASTA_OUTPUTS / "resumo_resultados.txt", "w", encoding="utf-8") as arquivo:
        arquivo.write("PROJETO ROTA INTELIGENTE - SABOR EXPRESS\n")
        arquivo.write("=" * 48 + "\n\n")
        arquivo.write("Entregas agrupadas em 3 zonas pelo K-Means.\n")
        arquivo.write("Cada zona recebe uma rota iniciando e terminando no CD.\n\n")
        for _, linha in df_rotas.iterrows():
            arquivo.write(
                f"Zona {int(linha['zona'])}: {linha['entregas']} | "
                f"Distancia: {linha['distancia_km']:.2f} km\n"
            )
            arquivo.write(f"Rota: {linha['rota_completa']}\n\n")
        arquivo.write(f"Distancia total das tres rotas: {distancia_total:.2f} km\n")
        arquivo.write("\nComparacao simples entre A*, BFS e DFS: CD ate K.\n")
        for _, linha in comparacao.iterrows():
            arquivo.write(
                f"{linha['algoritmo']}: {linha['caminho']} | "
                f"{linha['distancia_km']:.2f} km\n"
            )

    print("Projeto executado com sucesso.")
    print("\nRotas por zona:")
    print(df_rotas.to_string(index=False))
    print(f"\nDistancia total: {distancia_total:.2f} km")
    print("\nComparacao das buscas:")
    print(comparacao[["algoritmo", "caminho", "distancia_km"]].to_string(index=False))
    print("\nArquivos gerados na pasta outputs/ e docs/.")


if __name__ == "__main__":
    main()
