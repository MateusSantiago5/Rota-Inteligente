from grafo import caminho_astar


def montar_rota_grupo(grafo, base, destinos):
    """
    Monta uma rota simples: sempre escolhe a entrega ainda nao visitada
    que fica mais perto do ponto atual, calculando o trecho com A*.
    """
    faltam = set(destinos)
    atual = base
    rota_completa = [base]
    ordem_entregas = []
    distancia_total = 0.0

    while faltam:
        melhor_destino = None
        melhor_caminho = None
        melhor_distancia = float("inf")

        for destino in sorted(faltam):
            caminho, distancia = caminho_astar(grafo, atual, destino)
            if distancia < melhor_distancia:
                melhor_destino = destino
                melhor_caminho = caminho
                melhor_distancia = distancia

        rota_completa.extend(melhor_caminho[1:])
        ordem_entregas.append(melhor_destino)
        distancia_total += melhor_distancia
        atual = melhor_destino
        faltam.remove(melhor_destino)

    # Retorno ao centro de distribuicao.
    caminho_volta, distancia_volta = caminho_astar(grafo, atual, base)
    rota_completa.extend(caminho_volta[1:])
    distancia_total += distancia_volta

    return rota_completa, ordem_entregas, distancia_total
