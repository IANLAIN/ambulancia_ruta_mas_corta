# Atención de Emergencias: Rutas de Menor Distancia para Ambulancias (Dijkstra)

Sistema desarrollado en **Python 3.8+** para la asignatura **Estructura de Datos**. Modela la red vial de una ciudad como un **grafo ponderado no dirigido** (lista de adyacencia) y utiliza el **algoritmo de Dijkstra con cola de prioridad (`heapq`)** para asignar la ambulancia más cercana a una emergencia y trasladar al paciente al hospital más próximo por la ruta de menor distancia en kilómetros.

---

## Estructura del Proyecto

- `emergencias.py`: Implementación del grafo, algoritmo de Dijkstra, reconstrucción de caminos, despacho de ambulancias, demo por consola y ventana animada que muestra la emergencia, la elección de ambulancia y hospital, y el recorrido calle por calle.
- `pruebas.py`: Suite de pruebas unitarias (`unittest`) que valida rutas óptimas, casos límite, nodos aislados, pesos negativos y nodos inexistentes.
- `README.md`: Documentación del proyecto y verificación manual del grafo de ejemplo.

---

## Requisitos y Ejecución

El núcleo del sistema utiliza **exclusivamente la librería estándar de Python** (`heapq` y `math`).

### 1. Ejecutar la demostración principal
```bash
python3 emergencias.py
```

### 2. Ejecutar las pruebas automáticas
```bash
python3 pruebas.py
```

### 3. Visualización gráfica (opcional)
Si deseas abrir la ventana animada que muestra la emergencia, la elección de ambulancia y hospital, y el recorrido calle por calle:
```bash
pip install networkx matplotlib
python3 emergencias.py
```
*(Si no están instaladas, el programa funciona normalmente por consola e indica el comando de instalación).*

---

## Diseño del Grafo de Ejemplo y Verificación Manual

El grafo de demostración consta de **9 nodos**:
- **Bases de ambulancias:** `B1`, `B2`
- **Intersecciones:** `A`, `C`, `D`
- **Lugar de la emergencia:** `E`
- **Hospitales:** `H1`, `H2`
- **Zona aislada (sin conexión):** `Z`

### Calles (Aristas y Pesos en km)
- `(B1, E) = 10 km` *(calle directa larga)*
- `(B1, A) = 3 km`, `(A, C) = 2 km`, `(C, E) = 2 km` *(ruta con 3 calles pero de solo 7 km)*
- `(B2, D) = 6 km`, `(D, E) = 3 km` *(ruta desde B2 de 9 km)*
- `(E, H1) = 8 km` *(calle directa larga al Hospital H1)*
- `(D, H1) = 2 km` *(ruta `E -> D -> H1` de 2 calles y solo 5 km)*
- `(C, H2) = 6 km` *(ruta `E -> C -> H2` de 8 km)*
- `Z`: Nodo desconectado (`sin ruta`).

### Tabla de Verificación Manual (Dijkstra desde la Emergencia `E`)

| Nodo Destino | Rol | Ruta de Menor N.º de Calles | Ruta Óptima (Dijkstra) | Distancia Mínima (km) | Observación |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **`E`** | Emergencia | `E` (0 calles) | `E` | **0 km** | Nodo origen (`origen == destino`) |
| **`C`** | Intersección | `E -> C` (1 calle) | `E -> C` | **2 km** | Vecino directo |
| **`D`** | Intersección | `E -> D` (1 calle) | `E -> D` | **3 km** | Vecino directo |
| **`A`** | Intersección | `E -> C -> A` (2 calles) | `E -> C -> A` | **4 km** | `2 + 2 = 4 km` |
| **`H1`** | **Hospital 1 (Elegido)** | `E -> H1` (1 calle, 8 km) | `E -> D -> H1` | **5 km** | **Más corto por `D` (3 + 2 = 5 km < 8 km)** |
| **`B1`** | **Ambulancia 1 (Elegida)** | `B1 -> E` (1 calle, 10 km) | `B1 -> A -> C -> E` | **7 km** | **3 calles pero ahorra 3 km (3+2+2 = 7 km < 10 km)** |
| **`H2`** | Hospital 2 | `E -> C -> H2` (2 calles) | `E -> C -> H2` | **8 km** | Descartado frente a `H1` (8 km > 5 km) |
| **`B2`** | Ambulancia 2 | `B2 -> D -> E` (2 calles) | `B2 -> D -> E` | **9 km** | Descartada frente a `B1` (9 km > 7 km) |
| **`Z`** | Zona Aislada | Ninguna | `None` (*sin ruta*) | **∞** | Nodo aislado / inalcanzable |

### Salida Esperada por Consola
```text
Ambulancia B1: B1 -> A -> C -> E | 7 km
Hospital H1: E -> D -> H1 | 5 km
Total: 12 km
Sin ruta E -> Z
```
