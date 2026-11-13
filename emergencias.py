"""Sistema de rutas de menor distancia para ambulancias con Dijkstra."""

import heapq
import math

POSICIONES = {
    "B1": (0.0, 3.5),
    "A": (1.8, 2.0),
    "C": (3.8, 2.0),
    "E": (5.5, 3.5),
    "D": (7.5, 2.0),
    "H1": (9.5, 3.5),
    "Z": (0.5, 0.4),
    "H2": (3.8, 0.4),
    "B2": (7.5, 0.4),
}


def crear_grafo():
    """Crea y retorna un grafo vacío como diccionario."""
    return {}


def agregar_nodo(grafo, nodo):
    """Agrega un nodo al grafo si no existe."""
    if nodo not in grafo:
        grafo[nodo] = []


def agregar_calle(grafo, a, b, distancia):
    """Agrega una calle bidireccional con peso no negativo."""
    if distancia < 0:
        raise ValueError(f"La distancia no puede ser negativa: {distancia}")
    agregar_nodo(grafo, a)
    agregar_nodo(grafo, b)
    grafo[a].append((b, distancia))
    grafo[b].append((a, distancia))


def dijkstra(grafo, origen):
    """Calcula distancias mínimas y predecesores desde origen con Dijkstra."""
    if origen not in grafo:
        raise KeyError(f"El nodo de origen '{origen}' no existe en el grafo.")

    distancias = {nodo: math.inf for nodo in grafo}
    predecesores = {nodo: None for nodo in grafo}
    distancias[origen] = 0
    cola = [(0, origen)]

    while cola:
        dist_actual, actual = heapq.heappop(cola)

        # Ignorar entradas obsoletas del heap
        if dist_actual > distancias[actual]:
            continue

        # Orden fijo para resultados deterministas en empates
        for vecino, peso in sorted(grafo[actual]):
            if peso < 0:
                raise ValueError(f"Peso negativo detectado en arista ({actual}, {vecino}): {peso}")
            nueva_dist = dist_actual + peso
            if nueva_dist < distancias[vecino]:
                distancias[vecino] = nueva_dist
                predecesores[vecino] = actual
                heapq.heappush(cola, (nueva_dist, vecino))

    return distancias, predecesores


def reconstruir_ruta(predecesores, origen, destino):
    """Reconstruye la ruta desde origen hasta destino o retorna None."""
    if origen not in predecesores or destino not in predecesores:
        return None
    if origen == destino:
        return [origen]
    if predecesores[destino] is None:
        return None

    ruta = []
    actual = destino
    while actual is not None:
        ruta.append(actual)
        actual = predecesores[actual]

    ruta.reverse()
    return ruta if ruta[0] == origen else None


def hospital_mas_cercano(grafo, origen, hospitales):
    """Retorna el hospital más cercano, su distancia y la ruta."""
    if not hospitales:
        return None, math.inf, None

    distancias, predecesores = dijkstra(grafo, origen)
    mejor_hospital = None
    menor_distancia = math.inf

    for h in hospitales:
        if h in distancias and distancias[h] < menor_distancia:
            menor_distancia = distancias[h]
            mejor_hospital = h

    if mejor_hospital is None:
        return None, math.inf, None

    ruta = reconstruir_ruta(predecesores, origen, mejor_hospital)
    return mejor_hospital, menor_distancia, ruta


def atender_emergencia(grafo, ambulancias, lugar_emergencia, hospitales):
    """Asigna la ambulancia y el hospital más cercanos a la emergencia."""
    if lugar_emergencia not in grafo:
        print(f"Nodo inexistente: {lugar_emergencia}")
        return None

    dist_desde_emergencia, pred_desde_emergencia = dijkstra(grafo, lugar_emergencia)

    mejor_amb = None
    dist_amb = math.inf
    for amb in ambulancias:
        if amb in dist_desde_emergencia and dist_desde_emergencia[amb] < dist_amb:
            dist_amb = dist_desde_emergencia[amb]
            mejor_amb = amb

    if mejor_amb is None:
        print("Sin ruta a ambulancia")
        return None

    ruta_emergencia_a_amb = reconstruir_ruta(pred_desde_emergencia, lugar_emergencia, mejor_amb)
    ruta_amb_a_emergencia = list(reversed(ruta_emergencia_a_amb))

    mejor_hosp, dist_hosp, ruta_emergencia_a_hosp = hospital_mas_cercano(
        grafo, lugar_emergencia, hospitales
    )

    if mejor_hosp is None:
        print("Sin ruta a hospital")
        return None

    distancia_total = dist_amb + dist_hosp
    tramo_1 = " -> ".join(ruta_amb_a_emergencia)
    tramo_2 = " -> ".join(ruta_emergencia_a_hosp)

    print(f"Ambulancia {mejor_amb}: {tramo_1} | {dist_amb} km")
    print(f"Hospital {mejor_hosp}: {tramo_2} | {dist_hosp} km")
    print(f"Total: {distancia_total} km")

    return {
        "ambulancia": mejor_amb,
        "distancia_ambulancia": dist_amb,
        "ruta_ambulancia": ruta_amb_a_emergencia,
        "hospital": mejor_hosp,
        "distancia_hospital": dist_hosp,
        "ruta_hospital": ruta_emergencia_a_hosp,
        "distancia_total": distancia_total,
    }


def animar_ruta(
    grafo,
    ambulancias,
    emergencia,
    hospitales,
    resultado,
    pasos_por_tramo=15,
    intervalo_ms=50,
):
    """Anima paso a paso la decisión y el recorrido de la ambulancia."""
    try:
        from matplotlib.animation import FuncAnimation
        from matplotlib.patches import Patch
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        print("Falta instalar: pip install networkx matplotlib")
        return False

    G = nx.Graph()
    for nodo in grafo:
        G.add_node(nodo)
        for vecino, peso in grafo[nodo]:
            if not G.has_edge(nodo, vecino):
                G.add_edge(nodo, vecino, weight=peso)

    pos = {
        nodo: POSICIONES.get(nodo, (2.0 * i, -1.5))
        for i, nodo in enumerate(G.nodes())
    }

    dist_desde_e, _ = dijkstra(grafo, emergencia)

    fig, ax = plt.subplots(figsize=(11, 6))

    colores_nodos = []
    for n in G.nodes():
        if n == emergencia:
            colores_nodos.append("#ff6b6b")
        elif n in ambulancias:
            colores_nodos.append("#a6c8ff")
        elif n in hospitales:
            colores_nodos.append("#b2f2bb")
        elif len(grafo[n]) == 0:
            colores_nodos.append("#b0b0b0")
        else:
            colores_nodos.append("#e2e8f0")

    aristas = nx.draw_networkx_edges(G, pos, ax=ax, width=1.5, edge_color="#94a3b8")
    if aristas is not None:
        aristas.set_zorder(1)

    nodos_dibujados = nx.draw_networkx_nodes(
        G, pos, ax=ax, node_color=colores_nodos, node_size=950, edgecolors="black", linewidths=1.5
    )
    if nodos_dibujados is not None:
        nodos_dibujados.set_zorder(3)

    etiquetas_nodos = nx.draw_networkx_labels(
        G, pos, ax=ax, font_size=10, font_weight="bold"
    )
    for txt in etiquetas_nodos.values():
        txt.set_zorder(10)

    etiquetas_pesos = nx.get_edge_attributes(G, "weight")
    etiquetas_formateadas = {k: f"{v} km" for k, v in etiquetas_pesos.items()}
    textos_aristas = nx.draw_networkx_edge_labels(
        G,
        pos,
        ax=ax,
        edge_labels=etiquetas_formateadas,
        font_size=9,
        label_pos=0.5,
        bbox=dict(facecolor="white", edgecolor="none", pad=1),
    )
    for txt in textos_aristas.values():
        txt.set_zorder(6)

    leyenda_elementos = [
        Patch(facecolor="#a6c8ff", edgecolor="black", label="Base ambulancia"),
        Patch(facecolor="#ff6b6b", edgecolor="black", label="Emergencia"),
        Patch(facecolor="#b2f2bb", edgecolor="black", label="Hospital"),
        Patch(facecolor="#e2e8f0", edgecolor="black", label="Intersección"),
        Patch(facecolor="#b0b0b0", edgecolor="black", label="Zona aislada"),
    ]
    ax.legend(
        handles=leyenda_elementos,
        loc="lower left",
        fontsize=8.5,
        framealpha=0.95,
        ncol=2,
    )

    xe, ye = pos[emergencia]
    (aro_emergencia,) = ax.plot(
        [xe],
        [ye],
        marker="o",
        markersize=36,
        markerfacecolor="none",
        markeredgecolor="#c92a2a",
        markeredgewidth=3.0,
        zorder=4,
    )
    rotulo_emergencia = ax.text(
        xe,
        ye + (0.44 if ye >= 2.0 else -0.44),
        "EMERGENCIA",
        ha="center",
        va="center",
        fontsize=9.5,
        fontweight="bold",
        color="#c92a2a",
        bbox=dict(facecolor="#fff5f5", edgecolor="#c92a2a", pad=2),
        zorder=8,
    )

    amb_elegida = resultado["ambulancia"]
    dist_amb = resultado["distancia_ambulancia"]
    ruta_amb = resultado["ruta_ambulancia"]
    hosp_elegido = resultado["hospital"]
    dist_hosp = resultado["distancia_hospital"]
    ruta_hosp = resultado["ruta_hospital"]
    dist_total = resultado["distancia_total"]

    (aro_elegido,) = ax.plot(
        [],
        [],
        marker="o",
        markersize=35,
        markerfacecolor="none",
        markeredgecolor="#1864ab",
        markeredgewidth=3.0,
        zorder=4,
    )
    (nodos_atenuados,) = ax.plot(
        [],
        [],
        linestyle="none",
        marker="o",
        markersize=31,
        markerfacecolor="white",
        markeredgecolor="#adb5bd",
        alpha=0.65,
        zorder=3.5,
    )

    textos_amb = []
    for amb in ambulancias:
        if amb in pos:
            xa, ya = pos[amb]
            dy = 0.44 if ya >= 2.0 else -0.44
            d_val = dist_desde_e.get(amb, math.inf)
            txt_d = f"{amb}: {d_val} km" if d_val < math.inf else f"{amb}: sin ruta"
            es_elegida = amb == amb_elegida
            t = ax.text(
                xa,
                ya + dy,
                txt_d,
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold" if es_elegida else "normal",
                color="#1864ab" if es_elegida else "#495057",
                bbox=dict(
                    facecolor="#e7f5ff" if es_elegida else "#f8f9fa",
                    edgecolor="#1864ab" if es_elegida else "#adb5bd",
                    pad=2,
                ),
                visible=False,
                zorder=8,
            )
            textos_amb.append(t)

    textos_hosp = []
    for h in hospitales:
        if h in pos:
            xh, yh = pos[h]
            dy = 0.44 if yh >= 2.0 else -0.44
            d_val = dist_desde_e.get(h, math.inf)
            txt_d = f"{h}: {d_val} km" if d_val < math.inf else f"{h}: sin ruta"
            es_elegido = h == hosp_elegido
            t = ax.text(
                xh,
                yh + dy,
                txt_d,
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold" if es_elegido else "normal",
                color="#2b8a3e" if es_elegido else "#495057",
                bbox=dict(
                    facecolor="#ebfbee" if es_elegido else "#f8f9fa",
                    edgecolor="#2b8a3e" if es_elegido else "#adb5bd",
                    pad=2,
                ),
                visible=False,
                zorder=8,
            )
            textos_hosp.append(t)

    (linea_tramo1,) = ax.plot([], [], color="#d9534f", linewidth=4.0, zorder=2)
    (linea_tramo2,) = ax.plot([], [], color="#1f4e9c", linewidth=4.0, zorder=2)
    (ambulancia_mk,) = ax.plot(
        [],
        [],
        marker="s",
        color="#d9534f",
        markersize=9,
        markeredgecolor="black",
        zorder=7,
    )

    texto_km = ax.text(
        0.02,
        0.95,
        "Recorrido: 0.0 km",
        transform=ax.transAxes,
        fontsize=10.5,
        fontweight="bold",
        bbox=dict(facecolor="white", edgecolor="#94a3b8", pad=4),
        zorder=9,
    )
    texto_fase = ax.text(
        0.5,
        0.95,
        "",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="#1e293b",
        bbox=dict(facecolor="#f8fafc", edgecolor="#64748b", pad=4),
        zorder=9,
    )

    pausa_1_5s = max(1, int(1500 / intervalo_ms))
    pausa_2_0s = max(1, int(2000 / intervalo_ms))
    pausa_nodo = max(1, pasos_por_tramo // 3)

    cuadros = []

    for _ in range(pausa_1_5s):
        cuadros.append(
            {
                "fase": f"Emergencia en {emergencia}",
                "km": 0.0,
                "t1": ([], []),
                "t2": ([], []),
                "amb": None,
                "modo": "emergencia",
            }
        )

    for _ in range(pausa_2_0s):
        cuadros.append(
            {
                "fase": f"Ambulancia más cercana: {amb_elegida} ({dist_amb} km)",
                "km": 0.0,
                "t1": ([], []),
                "t2": ([], []),
                "amb": None,
                "modo": "eleccion_amb",
            }
        )

    km_acum = 0.0
    x_ini, y_ini = pos[ruta_amb[0]]
    xs_t1 = [x_ini]
    ys_t1 = [y_ini]

    for i in range(len(ruta_amb) - 1):
        u, v = ruta_amb[i], ruta_amb[i + 1]
        peso = dict(grafo[u])[v]
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        for paso in range(1, pasos_por_tramo + 1):
            frac = paso / pasos_por_tramo
            xa = x0 + frac * (x1 - x0)
            ya = y0 + frac * (y1 - y0)
            desp = 0.22 * abs(2 * frac - 1)
            cuadros.append(
                {
                    "fase": f"Ambulancia {amb_elegida} -> {emergencia} ({u} -> {v})",
                    "km": km_acum + frac * peso,
                    "t1": (xs_t1 + [xa], ys_t1 + [ya]),
                    "t2": ([], []),
                    "amb": (xa, ya + desp),
                    "modo": "ruta_1",
                }
            )
        km_acum += peso
        xs_t1.append(x1)
        ys_t1.append(y1)
        if i < len(ruta_amb) - 2:
            for _ in range(pausa_nodo):
                cuadros.append(
                    {
                        "fase": f"Ambulancia {amb_elegida} en intersección {v}",
                        "km": km_acum,
                        "t1": (list(xs_t1), list(ys_t1)),
                        "t2": ([], []),
                        "amb": (x1, y1 + 0.22),
                        "modo": "ruta_1",
                    }
                )

    for _ in range(pausa_1_5s):
        cuadros.append(
            {
                "fase": f"Paciente recogido en {emergencia}",
                "km": km_acum,
                "t1": (list(xs_t1), list(ys_t1)),
                "t2": ([], []),
                "amb": (pos[emergencia][0], pos[emergencia][1] + 0.22),
                "modo": "recogido",
            }
        )

    for _ in range(pausa_2_0s):
        cuadros.append(
            {
                "fase": f"Hospital más cercano: {hosp_elegido} ({dist_hosp} km)",
                "km": km_acum,
                "t1": (list(xs_t1), list(ys_t1)),
                "t2": ([], []),
                "amb": (pos[emergencia][0], pos[emergencia][1] + 0.22),
                "modo": "eleccion_hosp",
            }
        )

    x_ini2, y_ini2 = pos[ruta_hosp[0]]
    xs_t2 = [x_ini2]
    ys_t2 = [y_ini2]

    for i in range(len(ruta_hosp) - 1):
        u, v = ruta_hosp[i], ruta_hosp[i + 1]
        peso = dict(grafo[u])[v]
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        for paso in range(1, pasos_por_tramo + 1):
            frac = paso / pasos_por_tramo
            xa = x0 + frac * (x1 - x0)
            ya = y0 + frac * (y1 - y0)
            desp = 0.22 * abs(2 * frac - 1)
            cuadros.append(
                {
                    "fase": f"Traslado {emergencia} -> {hosp_elegido} ({u} -> {v})",
                    "km": km_acum + frac * peso,
                    "t1": (list(xs_t1), list(ys_t1)),
                    "t2": (xs_t2 + [xa], ys_t2 + [ya]),
                    "amb": (xa, ya + desp),
                    "modo": "ruta_2",
                }
            )
        km_acum += peso
        xs_t2.append(x1)
        ys_t2.append(y1)
        if i < len(ruta_hosp) - 2:
            for _ in range(pausa_nodo):
                cuadros.append(
                    {
                        "fase": f"Ambulancia en intersección {v}",
                        "km": km_acum,
                        "t1": (list(xs_t1), list(ys_t1)),
                        "t2": (list(xs_t2), list(ys_t2)),
                        "amb": (x1, y1 + 0.22),
                        "modo": "ruta_2",
                    }
                )

    for _ in range(pausa_1_5s):
        cuadros.append(
            {
                "fase": f"Llegada a {hosp_elegido} | Total: {dist_total} km",
                "km": float(dist_total),
                "t1": (list(xs_t1), list(ys_t1)),
                "t2": (list(xs_t2), list(ys_t2)),
                "amb": (pos[hosp_elegido][0], pos[hosp_elegido][1] + 0.22),
                "modo": "fin",
            }
        )

    def actualizar(idx):
        c = cuadros[idx]
        modo = c["modo"]
        texto_fase.set_text(c["fase"])
        texto_km.set_text(f"Recorrido: {c['km']:.1f} km")

        linea_tramo1.set_data(c["t1"][0], c["t1"][1])
        linea_tramo2.set_data(c["t2"][0], c["t2"][1])

        if c["amb"] is not None:
            ambulancia_mk.set_data([c["amb"][0]], [c["amb"][1]])
        else:
            ambulancia_mk.set_data([], [])

        aro_emergencia.set_visible(modo in ("emergencia", "recogido"))
        rotulo_emergencia.set_visible(modo == "emergencia")

        for t in textos_amb:
            t.set_visible(modo == "eleccion_amb")
        for t in textos_hosp:
            t.set_visible(modo == "eleccion_hosp")

        if modo == "eleccion_amb":
            aro_elegido.set_data([pos[amb_elegida][0]], [pos[amb_elegida][1]])
            aro_elegido.set_markeredgecolor("#1864ab")
            otros = [pos[a] for a in ambulancias if a != amb_elegida and a in pos]
            nodos_atenuados.set_data([p[0] for p in otros], [p[1] for p in otros])
        elif modo == "eleccion_hosp":
            aro_elegido.set_data([pos[hosp_elegido][0]], [pos[hosp_elegido][1]])
            aro_elegido.set_markeredgecolor("#2b8a3e")
            otros = [pos[h] for h in hospitales if h != hosp_elegido and h in pos]
            nodos_atenuados.set_data([p[0] for p in otros], [p[1] for p in otros])
        else:
            aro_elegido.set_data([], [])
            nodos_atenuados.set_data([], [])

        return (
            linea_tramo1,
            linea_tramo2,
            ambulancia_mk,
            texto_km,
            texto_fase,
            aro_emergencia,
            rotulo_emergencia,
            aro_elegido,
            nodos_atenuados,
        )

    ax.set_title("Recorrido de la ambulancia (Dijkstra)", fontsize=13, fontweight="bold")
    xs_all = [p[0] for p in pos.values()]
    ys_all = [p[1] for p in pos.values()]
    ax.set_xlim(min(xs_all) - 1.0, max(xs_all) + 1.0)
    ax.set_ylim(min(ys_all) - 0.85, max(ys_all) + 1.25)
    ax.axis("off")
    plt.tight_layout()

    animacion = FuncAnimation(
        fig,
        actualizar,
        frames=len(cuadros),
        interval=intervalo_ms,
        repeat=False,
        blit=False,
    )
    plt.show()
    return animacion


def construir_grafo_ejemplo():
    """Construye y retorna el grafo de ejemplo de 9 nodos."""
    grafo = crear_grafo()
    agregar_calle(grafo, "B1", "E", 10)
    agregar_calle(grafo, "B1", "A", 3)
    agregar_calle(grafo, "A", "C", 2)
    agregar_calle(grafo, "C", "E", 2)
    agregar_calle(grafo, "B2", "D", 6)
    agregar_calle(grafo, "D", "E", 3)
    agregar_calle(grafo, "E", "H1", 8)
    agregar_calle(grafo, "D", "H1", 2)
    agregar_calle(grafo, "C", "H2", 6)
    agregar_nodo(grafo, "Z")
    return grafo


if __name__ == "__main__":
    ciudad = construir_grafo_ejemplo()
    bases_ambulancia = ["B1", "B2"]
    hospitales_disponibles = ["H1", "H2"]
    nodo_emergencia = "E"

    resultado = atender_emergencia(
        ciudad, bases_ambulancia, nodo_emergencia, hospitales_disponibles
    )

    dist, pred = dijkstra(ciudad, "E")
    ruta_aislada = reconstruir_ruta(pred, "E", "Z")
    if ruta_aislada is None:
        print("Sin ruta E -> Z")

    if resultado:
        animacion = animar_ruta(
            ciudad,
            bases_ambulancia,
            nodo_emergencia,
            hospitales_disponibles,
            resultado,
        )
