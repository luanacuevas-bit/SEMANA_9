# deg_analysis.py - Analisis de degeneracion del BST (Actividad 2B)
# Compara la altura del arbol cuando insertamos en orden vs. al azar.
# Altura medida en ARISTAS (arbol vacio = -1, una sola hoja = 0),
# asi un arbol en cadena de n nodos tiene h = n-1.

import math
import random


class Nodo:
    def __init__(self, clave):
        self.clave = clave
        self.izq = self.der = None


def insertar(raiz, clave):
    if raiz is None:
        return Nodo(clave)
    if clave < raiz.clave:
        raiz.izq = insertar(raiz.izq, clave)
    elif clave > raiz.clave:
        raiz.der = insertar(raiz.der, clave)
    return raiz


def altura(raiz) -> int:
    if raiz is None:
        return -1
    return 1 + max(altura(raiz.izq), altura(raiz.der))


def construir(claves):
    raiz = None
    for c in claves:
        raiz = insertar(raiz, c)
    return raiz


random.seed(42)  # para que los resultados se repitan al exponer

REPETICIONES = 5

print(f"{'N':>6} | {'h_ord':>6} | {'h_ale':>6} | {'h_teo':>6} | {'ratio':>6}")
print("-" * 44)

for n in [10, 20, 50, 100]:
    claves = [f'UNAP-{i:04d}' for i in range(1, n + 1)]

    # 1) Insercion en orden ascendente -> arbol en cadena
    h_ord = altura(construir(claves))

    # 2) Insercion aleatoria: promedio de 5 repeticiones
    total = 0
    for _ in range(REPETICIONES):
        random.shuffle(claves)
        total += altura(construir(claves))
    h_ale = total / REPETICIONES

    # 3) Altura teorica esperada para arbol aleatorio
    h_teo = 1.39 * math.log2(n)

    ratio = h_ord / h_ale
    print(f"{n:>6} | {h_ord:>6} | {h_ale:>6.1f} | {h_teo:>6.1f} | {ratio:>6.1f}")

print()
print("Conclusion: en orden ascendente h = N-1 (cadena), el BST pierde su ventaja.")
print("Con datos al azar h crece como log2(N). Por eso hace falta un arbol balanceado (AVL, S10).")
