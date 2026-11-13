"""
Pruebas automáticas para el sistema de atención de emergencias (emergencias.py).
"""

import math
import unittest

from emergencias import (
    agregar_calle,
    agregar_nodo,
    atender_emergencia,
    construir_grafo_ejemplo,
    crear_grafo,
    dijkstra,
    hospital_mas_cercano,
    reconstruir_ruta,
)


class PruebasSistemaEmergencias(unittest.TestCase):
    def setUp(self):
        self.grafo = construir_grafo_ejemplo()

    def test_1_ruta_y_distancia_grafo_ejemplo(self):
        """1. Verifica ruta y distancias calculadas a mano en el grafo de ejemplo."""
        distancias, predecesores = dijkstra(self.grafo, "E")

        # Distancias esperadas desde E calculadas a mano
        esperadas = {
            "E": 0,
            "C": 2,
            "D": 3,
            "A": 4,
            "H1": 5,
            "B1": 7,
            "H2": 8,
            "B2": 9,
            "Z": math.inf,
        }
        self.assertEqual(distancias, esperadas)

        # Verificación del flujo completo de atención de emergencia
        res = atender_emergencia(self.grafo, ["B1", "B2"], "E", ["H1", "H2"])
        self.assertIsNotNone(res)
        self.assertEqual(res["ambulancia"], "B1")
        self.assertEqual(res["distancia_ambulancia"], 7)
        self.assertEqual(res["ruta_ambulancia"], ["B1", "A", "C", "E"])
        self.assertEqual(res["hospital"], "H1")
        self.assertEqual(res["distancia_hospital"], 5)
        self.assertEqual(res["ruta_hospital"], ["E", "D", "H1"])
        self.assertEqual(res["distancia_total"], 12)

    def test_2_ruta_menor_distancia_con_mas_nodos(self):
        """2. Dijkstra elige la ruta de menor distancia en km aunque tenga más calles."""
        # Entre B1 y E existe calle directa de 10 km (1 arista),
        # pero B1 -> A -> C -> E tiene 3 aristas y suma 3 + 2 + 2 = 7 km.
        distancias, predecesores = dijkstra(self.grafo, "B1")
        ruta = reconstruir_ruta(predecesores, "B1", "E")
        self.assertEqual(distancias["E"], 7)
        self.assertEqual(ruta, ["B1", "A", "C", "E"])
        self.assertGreater(len(ruta), 2)

    def test_3_origen_igual_a_destino(self):
        """3. Cuando el origen es igual al destino, la distancia es 0 y la ruta es [origen]."""
        distancias, predecesores = dijkstra(self.grafo, "B1")
        ruta = reconstruir_ruta(predecesores, "B1", "B1")
        self.assertEqual(distancias["B1"], 0)
        self.assertEqual(ruta, ["B1"])

    def test_4_nodo_aislado_sin_ruta(self):
        """4. Un nodo aislado o desconectado tiene distancia infinita y ruta None ('sin ruta')."""
        distancias, predecesores = dijkstra(self.grafo, "E")
        ruta = reconstruir_ruta(predecesores, "E", "Z")
        self.assertEqual(distancias["Z"], math.inf)
        self.assertIsNone(ruta)

        # También si la emergencia ocurre en el nodo aislado Z
        res = atender_emergencia(self.grafo, ["B1", "B2"], "Z", ["H1", "H2"])
        self.assertIsNone(res)

    def test_5_eleccion_hospital_mas_cercano(self):
        """5. Con dos hospitales a distinta distancia, elige el más cercano (H1 a 5 km vs H2 a 8 km)."""
        hospital, distancia, ruta = hospital_mas_cercano(self.grafo, "E", ["H2", "H1"])
        self.assertEqual(hospital, "H1")
        self.assertEqual(distancia, 5)
        self.assertEqual(ruta, ["E", "D", "H1"])

    def test_6_peso_negativo_lanza_value_error(self):
        """6. Intentar agregar o procesar una calle con peso negativo lanza ValueError."""
        g = crear_grafo()
        with self.assertRaises(ValueError):
            agregar_calle(g, "X", "Y", -4)

        # Incluso si alguien altera la estructura manualmente con un peso negativo
        g["X"] = [("Y", -2)]
        g["Y"] = [("X", -2)]
        with self.assertRaises(ValueError):
            dijkstra(g, "X")

    def test_7_nodo_inexistente_se_maneja_correctamente(self):
        """7. Nodos inexistentes son manejados mediante excepción clara o retorno controlado."""
        with self.assertRaises(KeyError):
            dijkstra(self.grafo, "NODO_FANTASMA")

        _, predecesores = dijkstra(self.grafo, "E")
        self.assertIsNone(reconstruir_ruta(predecesores, "E", "NODO_FANTASMA"))
        self.assertIsNone(atender_emergencia(self.grafo, ["B1"], "NODO_FANTASMA", ["H1"]))

    def test_8_empate_entre_rutas_de_igual_distancia(self):
        """Prueba adicional: manejo determinista de empates entre dos rutas de igual distancia."""
        g = crear_grafo()
        agregar_calle(g, "Inicio", "Camino1", 5)
        agregar_calle(g, "Camino1", "Fin", 5)
        agregar_calle(g, "Inicio", "Camino2", 5)
        agregar_calle(g, "Camino2", "Fin", 5)

        distancias, predecesores = dijkstra(g, "Inicio")
        ruta = reconstruir_ruta(predecesores, "Inicio", "Fin")
        self.assertEqual(distancias["Fin"], 10)
        self.assertIn(ruta, [["Inicio", "Camino1", "Fin"], ["Inicio", "Camino2", "Fin"]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
