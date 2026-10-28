# bst_gui.py - Entorno gráfico del BST de estudiantes UNAP (Python 3.12, tkinter)
#
# Usa la misma lógica de la práctica (insertar, buscar, eliminar con 3 casos,
# inorden y altura en aristas) pero con un árbol que se dibuja en pantalla.
#
# Ejecutar:  python bst_gui.py
# tkinter viene incluido con Python en Windows; no hay que instalar nada.

import random
import time
from dataclasses import dataclass
from typing import Optional

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:          # permite importar la lógica sin tkinter (pruebas)
    tk = ttk = messagebox = None


# =====================================================================
#  LÓGICA DEL BST (la misma idea de bst_unap.cpp y siga_consulta.py)
# =====================================================================
@dataclass
class Estudiante:
    codigo: str
    nombre: str
    escuela: str


class Nodo:
    def __init__(self, dato: Estudiante):
        self.dato = dato
        self.izq = None
        self.der = None


class BST:
    def __init__(self):
        self.raiz = None
        self.cantidad = 0
        self.total_ops = 0

    # ---------- insertar: baja hasta un hueco y ahí crea el nodo ----------
    def insertar(self, est: Estudiante) -> bool:
        self.total_ops += 1
        self.raiz, insertado = self._insertar(self.raiz, est)
        if insertado:
            self.cantidad += 1
        return insertado

    def _insertar(self, nodo, est):
        if nodo is None:
            return Nodo(est), True
        if est.codigo < nodo.dato.codigo:
            nodo.izq, ok = self._insertar(nodo.izq, est)
        elif est.codigo > nodo.dato.codigo:
            nodo.der, ok = self._insertar(nodo.der, est)
        else:
            ok = False                      # código repetido: no se inserta
        return nodo, ok

    # ---------- buscar: devuelve (estudiante o None, camino recorrido) ----------
    def buscar(self, codigo: str):
        self.total_ops += 1
        camino = []
        nodo = self.raiz
        while nodo is not None:
            camino.append(nodo.dato.codigo)
            if codigo == nodo.dato.codigo:
                return nodo.dato, camino
            nodo = nodo.izq if codigo < nodo.dato.codigo else nodo.der
        return None, camino

    def obtener(self, codigo: str) -> Optional[Estudiante]:
        """Busca sin contar como operación (para clics en el dibujo)."""
        nodo = self.raiz
        while nodo is not None:
            if codigo == nodo.dato.codigo:
                return nodo.dato
            nodo = nodo.izq if codigo < nodo.dato.codigo else nodo.der
        return None

    # ---------- eliminar: hoja, un hijo o dos hijos ----------
    def eliminar(self, codigo: str) -> bool:
        self.total_ops += 1
        self.raiz, eliminado = self._eliminar(self.raiz, codigo)
        if eliminado:
            self.cantidad -= 1
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
        if nodo.izq is None:                # hoja o solo hijo derecho
            return nodo.der, True
        if nodo.der is None:                # solo hijo izquierdo
            return nodo.izq, True
        suc = nodo.der                      # dos hijos: sucesor = menor de la derecha
        while suc.izq is not None:
            suc = suc.izq
        nodo.dato = suc.dato
        nodo.der, _ = self._eliminar(nodo.der, suc.dato.codigo)
        return nodo, True

    # ---------- listar en orden (inorden) ----------
    def listar(self) -> list:
        resultado = []
        self._inorden(self.raiz, resultado)
        return resultado

    def _inorden(self, nodo, resultado):
        if nodo is None:
            return
        self._inorden(nodo.izq, resultado)
        resultado.append(nodo.dato)
        self._inorden(nodo.der, resultado)

    # ---------- altura en aristas (vacío = -1, una hoja = 0) ----------
    def altura(self) -> int:
        return self._altura(self.raiz)

    def _altura(self, nodo) -> int:
        if nodo is None:
            return -1
        return 1 + max(self._altura(nodo.izq), self._altura(nodo.der))

    def limpiar(self):
        self.raiz = None
        self.cantidad = 0

    # ---------- posiciones para dibujar ----------
    # columna = lugar del nodo en el recorrido inorden; fila = profundidad.
    # Así los nodos nunca se tapan entre sí.
    def posiciones(self):
        """Devuelve lista de (codigo, columna, fila, codigo_del_padre)."""
        resultado = []
        contador = [0]

        def recorrer(nodo, fila, padre):
            if nodo is None:
                return
            recorrer(nodo.izq, fila + 1, nodo.dato.codigo)
            col = contador[0]
            contador[0] += 1
            resultado.append((nodo.dato.codigo, col, fila, padre))
            recorrer(nodo.der, fila + 1, nodo.dato.codigo)

        recorrer(self.raiz, 0, None)
        return resultado


def etiqueta(codigo: str) -> str:
    """Texto corto para el nodo: UNAP-2023-000050 -> 23-50."""
    partes = codigo.split('-')
    if len(partes) == 3 and partes[1].isdigit() and partes[2].isdigit():
        return f'{partes[1][-2:]}-{int(partes[2])}'
    return partes[-1][-6:]


def generar_estudiantes(n: int) -> list:
    escuelas = ['Ing. Sistemas', 'Ing. Civil', 'IACD', 'Medicina', 'Derecho']
    nombres = ['Mamani', 'Quispe', 'Condori', 'Apaza', 'Huanca', 'Ticona', 'Ccopa']
    lista, usados = [], set()
    while len(lista) < n:
        cod = f'UNAP-{random.randint(2018, 2024)}-{random.randint(1, 9999):06d}'
        if cod in usados:
            continue
        usados.add(cod)
        lista.append(Estudiante(
            cod, f'{random.choice(nombres)} {random.choice(nombres)}, J.',
            random.choice(escuelas)))
    return lista


# =====================================================================
#  INTERFAZ GRÁFICA
# =====================================================================
COLOR_NORMAL = '#BBDEFB'
COLOR_CAMINO = '#FFF176'
COLOR_ENCONTRADO = '#FFB74D'
COLOR_NUEVO = '#A5D6A7'
COLOR_LINEA = '#607D8B'

RADIO = 24
DX = 52        # separación horizontal entre columnas
DY = 76        # separación vertical entre niveles
MARGEN = 44


class App:
    def __init__(self, root):
        self.root = root
        self.bst = BST()
        self.resaltados = {}          # codigo -> color
        self.mensaje = 'Listo'
        self.ms = 0.0

        root.title('SIGA-UNAP — Árbol Binario de Búsqueda (SIS210 · S09)')
        root.geometry('1100x680')
        root.minsize(900, 560)

        self.v_codigo = tk.StringVar()
        self.v_nombre = tk.StringVar()
        self.v_escuela = tk.StringVar()

        self._crear_panel_izquierdo()
        self._crear_lienzo()
        self._crear_barra_estado()

        # árbol inicial: los 5 estudiantes de la práctica
        for cod, nom, esc in [
            ('UNAP-2023-000050', 'Mamani Quispe, Juan', 'Ing. Sistemas'),
            ('UNAP-2022-000030', 'Flores Condori, Ana', 'Ing. Civil'),
            ('UNAP-2024-000070', 'Ticona Apaza, Carlos', 'IACD'),
            ('UNAP-2021-000020', 'Huanca Puma, Lucia', 'Ing. Electrica'),
            ('UNAP-2023-000040', 'Ccopa Ramos, Pedro', 'Ing. Sistemas'),
        ]:
            self.bst.insertar(Estudiante(cod, nom, esc))
        self.bst.total_ops = 0
        self.refrescar()

    # ------------------------- construcción de la ventana -------------------------
    def _crear_panel_izquierdo(self):
        izq = ttk.Frame(self.root, padding=8)
        izq.pack(side='left', fill='y')

        marco = ttk.LabelFrame(izq, text='Estudiante', padding=8)
        marco.pack(fill='x')
        for i, (texto, var) in enumerate([('Código', self.v_codigo),
                                          ('Nombre', self.v_nombre),
                                          ('Escuela', self.v_escuela)]):
            ttk.Label(marco, text=texto).grid(row=i, column=0, sticky='w', pady=2)
            ttk.Entry(marco, textvariable=var, width=26).grid(row=i, column=1, pady=2, padx=(6, 0))
        ttk.Label(marco, text='Ej.: UNAP-2024-000010', foreground='#777').grid(
            row=3, column=1, sticky='w')

        ops = ttk.LabelFrame(izq, text='Operaciones', padding=8)
        ops.pack(fill='x', pady=(8, 0))
        botones = [
            ('Insertar', self.accion_insertar),
            ('Buscar', self.accion_buscar),
            ('Eliminar', self.accion_eliminar),
            ('Limpiar árbol', self.accion_limpiar),
        ]
        for i, (texto, cmd) in enumerate(botones):
            ttk.Button(ops, text=texto, command=cmd).grid(
                row=i // 2, column=i % 2, sticky='ew', padx=2, pady=2)
        ops.columnconfigure(0, weight=1)
        ops.columnconfigure(1, weight=1)

        demo = ttk.LabelFrame(izq, text='Cargar datos / demostración', padding=8)
        demo.pack(fill='x', pady=(8, 0))
        ttk.Button(demo, text='Agregar 20 estudiantes al azar',
                   command=self.accion_cargar_20).pack(fill='x', pady=2)
        ttk.Button(demo, text='Demo: 15 códigos en ORDEN (degenera)',
                   command=lambda: self.accion_demo(ordenado=True)).pack(fill='x', pady=2)
        ttk.Button(demo, text='Demo: 15 códigos al AZAR',
                   command=lambda: self.accion_demo(ordenado=False)).pack(fill='x', pady=2)

        lst = ttk.LabelFrame(izq, text='Listado en orden (inorden)', padding=6)
        lst.pack(fill='both', expand=True, pady=(8, 0))
        sb = ttk.Scrollbar(lst, orient='vertical')
        self.lista = tk.Listbox(lst, width=40, height=10, yscrollcommand=sb.set,
                                font=('Consolas', 9), activestyle='none')
        sb.config(command=self.lista.yview)
        sb.pack(side='right', fill='y')
        self.lista.pack(side='left', fill='both', expand=True)

    def _crear_lienzo(self):
        der = ttk.Frame(self.root, padding=(0, 8, 8, 8))
        der.pack(side='left', fill='both', expand=True)

        leyenda = ttk.Frame(der)
        leyenda.pack(fill='x')
        for color, texto in [(COLOR_CAMINO, 'camino recorrido'),
                             (COLOR_ENCONTRADO, 'encontrado'),
                             (COLOR_NUEVO, 'recién insertado')]:
            tk.Label(leyenda, bg=color, width=2, relief='solid', bd=1).pack(side='left', padx=(0, 3))
            ttk.Label(leyenda, text=texto).pack(side='left', padx=(0, 12))
        ttk.Label(leyenda, text='(clic en un nodo para copiar sus datos)',
                  foreground='#777').pack(side='right')

        cuerpo = ttk.Frame(der)
        cuerpo.pack(fill='both', expand=True, pady=(4, 0))
        self.canvas = tk.Canvas(cuerpo, bg='white', highlightthickness=1,
                                highlightbackground='#BDBDBD')
        sx = ttk.Scrollbar(cuerpo, orient='horizontal', command=self.canvas.xview)
        sy = ttk.Scrollbar(cuerpo, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
        sx.pack(side='bottom', fill='x')
        sy.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

    def _crear_barra_estado(self):
        self.estado = ttk.Label(self.root, anchor='w', relief='sunken', padding=(8, 3))
        self.estado.pack(side='bottom', fill='x')

    # ------------------------- dibujo -------------------------
    def refrescar(self):
        self.dibujar()
        self.lista.delete(0, 'end')
        for e in self.bst.listar():
            self.lista.insert('end', f'{e.codigo}  {e.nombre}')
        self.estado.config(text=(
            f'Nodos: {self.bst.cantidad}   |   Altura: {self.bst.altura()}   |   '
            f'Operaciones: {self.bst.total_ops}   |   {self.mensaje}   ({self.ms:.3f} ms)'))

    def dibujar(self):
        c = self.canvas
        c.delete('all')
        pos = self.bst.posiciones()
        if not pos:
            c.create_text(300, 120, text='El árbol está vacío', fill='#999', font=('Arial', 14))
            c.configure(scrollregion=(0, 0, 600, 240))
            return
        xy = {cod: (MARGEN + col * DX, MARGEN + fila * DY) for cod, col, fila, _ in pos}

        for cod, _, _, padre in pos:                       # primero las líneas
            if padre is not None:
                (x1, y1), (x2, y2) = xy[padre], xy[cod]
                c.create_line(x1, y1, x2, y2, fill=COLOR_LINEA, width=2)

        for cod, _, _, _ in pos:                           # luego los nodos
            x, y = xy[cod]
            color = self.resaltados.get(cod, COLOR_NORMAL)
            c.create_oval(x - RADIO, y - RADIO, x + RADIO, y + RADIO,
                          fill=color, outline=COLOR_LINEA, width=2, tags=(f'n_{cod}',))
            c.create_text(x, y, text=etiqueta(cod), font=('Arial', 8, 'bold'),
                          tags=(f'n_{cod}',))
            c.tag_bind(f'n_{cod}', '<Button-1>', lambda ev, k=cod: self.seleccionar(k))

        x0, y0, x1, y1 = c.bbox('all')
        c.configure(scrollregion=(0, 0, x1 + MARGEN, y1 + MARGEN))

    def seleccionar(self, codigo):
        e = self.bst.obtener(codigo)
        if e:
            self.v_codigo.set(e.codigo)
            self.v_nombre.set(e.nombre)
            self.v_escuela.set(e.escuela)

    # ------------------------- acciones -------------------------
    def _terminar(self, mensaje, t0, resaltados=None):
        self.ms = (time.perf_counter() - t0) * 1000
        self.mensaje = mensaje
        self.resaltados = resaltados or {}
        self.refrescar()

    def accion_insertar(self):
        cod = self.v_codigo.get().strip()
        if not cod:
            messagebox.showwarning('Falta el código', 'Escribe un código para insertar.')
            return
        est = Estudiante(cod, self.v_nombre.get().strip() or '(sin nombre)',
                         self.v_escuela.get().strip() or '(sin escuela)')
        t0 = time.perf_counter()
        ok = self.bst.insertar(est)
        if ok:
            self._terminar(f'Insertado {cod}', t0, {cod: COLOR_NUEVO})
        else:
            self._terminar(f'El código {cod} ya existe (no se repite)', t0)

    def accion_buscar(self):
        cod = self.v_codigo.get().strip()
        if not cod:
            messagebox.showwarning('Falta el código', 'Escribe un código para buscar.')
            return
        t0 = time.perf_counter()
        est, camino = self.bst.buscar(cod)
        marcas = {k: COLOR_CAMINO for k in camino}
        if est:
            marcas[cod] = COLOR_ENCONTRADO
            self.v_nombre.set(est.nombre)
            self.v_escuela.set(est.escuela)
            self._terminar(f'Encontrado: {est.nombre} ({len(camino)} comparaciones)', t0, marcas)
        else:
            self._terminar(f'No encontrado ({len(camino)} comparaciones)', t0, marcas)

    def accion_eliminar(self):
        cod = self.v_codigo.get().strip()
        if not cod:
            messagebox.showwarning('Falta el código', 'Escribe un código para eliminar.')
            return
        t0 = time.perf_counter()
        ok = self.bst.eliminar(cod)
        self._terminar(f'Eliminado {cod}' if ok else f'No existe {cod}', t0)

    def accion_limpiar(self):
        t0 = time.perf_counter()
        self.bst.limpiar()
        self._terminar('Árbol vaciado', t0)

    def accion_cargar_20(self):
        t0 = time.perf_counter()
        for e in generar_estudiantes(20):
            self.bst.insertar(e)
        self._terminar('Se agregaron 20 estudiantes al azar', t0)

    def accion_demo(self, ordenado: bool):
        codigos = [f'UNAP-2024-{i:06d}' for i in range(1, 16)]
        if not ordenado:
            random.shuffle(codigos)
        t0 = time.perf_counter()
        self.bst.limpiar()
        for cod in codigos:
            self.bst.insertar(Estudiante(cod, f'Estudiante {cod[-3:]}', 'Ing. Sistemas'))
        h = self.bst.altura()
        if ordenado:
            msg = f'15 códigos en orden: altura {h} = N-1 (el árbol es una cadena)'
        else:
            msg = f'15 códigos al azar: altura {h} (mucho menor que 14)'
        self._terminar(msg, t0)


def main():
    if tk is None:
        raise SystemExit('Este equipo no tiene tkinter instalado.')
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
