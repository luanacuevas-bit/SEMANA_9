# siga_consulta.py - Simulacion del modulo de consulta del SIGA-UNAP (Actividad 3)
# Usa un BST donde la clave es el codigo del estudiante.

import time
import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Estudiante:
    codigo: str
    nombre: str
    escuela: str
    ciclo: int


@dataclass
class Nodo:
    dato: Estudiante
    izq: Optional['Nodo'] = field(default=None, repr=False)
    der: Optional['Nodo'] = field(default=None, repr=False)


class SIGA_BST:
    def __init__(self):
        self.raiz = None
        self.total_ops = 0

    # ---------- insertar ----------
    def insertar(self, est: Estudiante) -> None:
        self.raiz = self._insertar(self.raiz, est)
        self.total_ops += 1

    def _insertar(self, nodo, est):
        if nodo is None:                       # hueco: aqui va el nuevo nodo
            return Nodo(est)
        if est.codigo < nodo.dato.codigo:
            nodo.izq = self._insertar(nodo.izq, est)
        elif est.codigo > nodo.dato.codigo:
            nodo.der = self._insertar(nodo.der, est)
        return nodo                            # si es igual, no se repite

    # ---------- buscar ----------
    def buscar(self, codigo: str) -> Optional[Estudiante]:
        self.total_ops += 1
        nodo = self.raiz
        while nodo is not None:
            if codigo == nodo.dato.codigo:
                return nodo.dato
            nodo = nodo.izq if codigo < nodo.dato.codigo else nodo.der
        return None

    # ---------- eliminar ----------
    def eliminar(self, codigo: str) -> bool:
        self.total_ops += 1
        self.raiz, eliminado = self._eliminar(self.raiz, codigo)
        return eliminado

    def _eliminar(self, nodo, codigo):
        if nodo is None:
            return None, False
        if codigo < nodo.dato.codigo:
            nodo.izq, ok = self._eliminar(nodo.izq, codigo)
            return nodo, ok
        if codigo > nodo.dato.codigo:
            nodo.der, ok = self._eliminar(nodo.der, codigo)
            return nodo, ok
        # Encontrado: tres casos
        if nodo.izq is None:                   # hoja o solo hijo derecho
            return nodo.der, True
        if nodo.der is None:                   # solo hijo izquierdo
            return nodo.izq, True
        # dos hijos: el sucesor es el menor del lado derecho
        suc = nodo.der
        while suc.izq is not None:
            suc = suc.izq
        nodo.dato = suc.dato
        nodo.der, _ = self._eliminar(nodo.der, suc.dato.codigo)
        return nodo, True

    # ---------- listar (inorden) ----------
    def listar(self) -> list[Estudiante]:
        resultado = []
        self._inorden(self.raiz, resultado)
        return resultado

    def _inorden(self, nodo, resultado):
        if nodo is None:
            return
        self._inorden(nodo.izq, resultado)     # izquierda
        resultado.append(nodo.dato)            # yo
        self._inorden(nodo.der, resultado)     # derecha

    # ---------- altura (en aristas: vacio = -1, una hoja = 0) ----------
    def altura(self) -> int:
        return self._altura(self.raiz)

    def _altura(self, nodo) -> int:
        if nodo is None:
            return -1
        return 1 + max(self._altura(nodo.izq), self._altura(nodo.der))


def generar_estudiantes(n: int) -> list[Estudiante]:
    escuelas = ['Ing. Sistemas', 'Ing. Civil', 'IACD', 'Medicina', 'Derecho']
    nombres = ['Mamani', 'Quispe', 'Condori', 'Apaza', 'Huanca', 'Ticona', 'Ccopa']
    estudiantes = []
    usados = set()                             # para no repetir codigos
    while len(estudiantes) < n:
        codigo = f'UNAP-{random.randint(2018, 2024)}-{random.randint(1, 9999):06d}'
        if codigo in usados:
            continue
        usados.add(codigo)
        estudiantes.append(Estudiante(
            codigo=codigo,
            nombre=f'{random.choice(nombres)} {random.choice(nombres)}, J.',
            escuela=random.choice(escuelas),
            ciclo=random.randint(1, 10),
        ))
    return estudiantes


def menu():
    siga = SIGA_BST()
    for est in generar_estudiantes(20):
        siga.insertar(est)
    siga.total_ops = 0                         # la carga inicial no cuenta como operacion del usuario
    print(f'SIGA-UNAP iniciado con 20 registros. Altura del árbol: {siga.altura()}')

    while True:
        print('\n[1] Buscar  [2] Listar  [3] Insertar  [4] Eliminar  [5] Salir')
        opcion = input('Opción: ').strip()

        if opcion == '5':
            print(f'Total operaciones: {siga.total_ops}')
            print(f'Altura final del árbol: {siga.altura()}')
            break

        t0 = time.perf_counter()

        if opcion == '1':
            cod = input('Código: ').strip()
            t0 = time.perf_counter()
            e = siga.buscar(cod)
            t1 = time.perf_counter()
            print(f'{e.nombre} ({e.escuela})' if e else 'No encontrado')
        elif opcion == '2':
            t0 = time.perf_counter()
            lista = siga.listar()
            t1 = time.perf_counter()
            for e in lista:
                print(f'  {e.codigo} - {e.nombre}')
        elif opcion == '3':
            cod = input('Código nuevo: ').strip()
            nom = input('Nombre: ').strip()
            esc = input('Escuela: ').strip()
            t0 = time.perf_counter()
            siga.insertar(Estudiante(cod, nom, esc, 1))
            t1 = time.perf_counter()
            print('Insertado')
        elif opcion == '4':
            cod = input('Código a eliminar: ').strip()
            t0 = time.perf_counter()
            ok = siga.eliminar(cod)
            t1 = time.perf_counter()
            print('Eliminado' if ok else 'No encontrado')
        else:
            print('Opción no válida')
            continue

        # el tiempo se mide solo sobre la operacion, sin esperar al teclado
        print(f'Tiempo: {(t1 - t0) * 1000:.3f} ms')


if __name__ == '__main__':
    menu()
