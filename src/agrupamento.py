import pandas as pd
from sklearn.cluster import KMeans


def agrupar_entregas(entregas: pd.DataFrame, pontos: pd.DataFrame, n_grupos=3):
    """Agrupa pedidos proximos usando as coordenadas x e y dos pontos."""
    dados = entregas.merge(pontos[["no", "x", "y"]], on="no", how="left")

    modelo = KMeans(n_clusters=n_grupos, random_state=42, n_init=10)
    dados["grupo"] = modelo.fit_predict(dados[["x", "y"]]) + 1

    return dados, modelo
