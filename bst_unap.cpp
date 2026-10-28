// bst_unap.cpp - Arbol Binario de Busqueda de estudiantes UNAP
// Version "limpia": SIN libreria std (nada de std::string, vector, unique_ptr, cout).
// Solo usamos punteros, arreglos de char y printf/strcmp (libreria C).
//
// Compilar: g++ -std=c++17 -Wall bst_unap.cpp -o bst_unap
// Ejecutar: ./bst_unap

#include <stdio.h>    // printf
#include <string.h>   // strcmp, strcpy

// Un estudiante: tres textos de tamano fijo (sin std::string)
struct Estudiante {
    char codigo[32];
    char nombre[64];
    char escuela[32];
};

// Un nodo del arbol: guarda un estudiante y dos punteros (izquierda y derecha)
struct Nodo {
    Estudiante dato;
    Nodo* izq;
    Nodo* der;
    Nodo(const Estudiante& e) : dato(e), izq(nullptr), der(nullptr) {}
};

class BST_UNAP {
    Nodo* raiz_;
    int cantidad_;   // cuantos estudiantes hay en el arbol

    // ---------------------------------------------------------------
    // TODO 1: insertar_aux
    // Precondicion: -
    // Postcondicion: el estudiante queda insertado como hoja y el arbol
    //                sigue cumpliendo la propiedad BST (izq < nodo < der).
    //                Si el codigo ya existe, no se inserta.
    // Complejidad: O(h), h = altura del arbol
    // Idea: bajamos comparando codigos hasta encontrar un hueco (nullptr).
    // ---------------------------------------------------------------
    void insertar_aux(Nodo*& nodo, const Estudiante& e) {
        if (nodo == nullptr) {            // hueco encontrado: crear nodo aqui
            nodo = new Nodo(e);
            cantidad_++;
            return;
        }
        int c = strcmp(e.codigo, nodo->dato.codigo);
        if (c < 0)      insertar_aux(nodo->izq, e);   // menor -> izquierda
        else if (c > 0) insertar_aux(nodo->der, e);   // mayor -> derecha
        // c == 0: codigo repetido, no hacemos nada
    }

    // ---------------------------------------------------------------
    // TODO 2: buscar_aux
    // Precondicion: -
    // Postcondicion: devuelve el puntero al nodo con ese codigo, o nullptr
    //                si no existe. No modifica el arbol.
    // Complejidad: O(h)
    // Idea: si es menor voy a la izquierda, si es mayor a la derecha.
    // ---------------------------------------------------------------
    Nodo* buscar_aux(Nodo* nodo, const char* cod) const {
        if (nodo == nullptr) return nullptr;          // no esta
        int c = strcmp(cod, nodo->dato.codigo);
        if (c == 0) return nodo;                      // lo encontre
        if (c < 0)  return buscar_aux(nodo->izq, cod);
        return buscar_aux(nodo->der, cod);
    }

    // ---------------------------------------------------------------
    // TODO 3: inorden_aux
    // Precondicion: 'resultado' tiene espacio para todos los estudiantes
    // Postcondicion: 'resultado' queda con los estudiantes ordenados por
    //                codigo (de menor a mayor); n = cuantos se guardaron.
    // Complejidad: O(n), visita cada nodo una vez
    // Idea: izquierda -> yo -> derecha
    // ---------------------------------------------------------------
    void inorden_aux(Nodo* nodo, Estudiante* resultado, int& n) const {
        if (nodo == nullptr) return;
        inorden_aux(nodo->izq, resultado, n);   // 1) todo lo menor
        resultado[n] = nodo->dato;              // 2) yo
        n++;
        inorden_aux(nodo->der, resultado, n);   // 3) todo lo mayor
    }

    // Minimo de un subarbol: el nodo mas a la izquierda. Complejidad O(h)
    Nodo* minimo(Nodo* nodo) const {
        while (nodo->izq != nullptr) nodo = nodo->izq;
        return nodo;
    }

    // ---------------------------------------------------------------
    // eliminar_aux (Actividad 2A) - tres casos
    // Precondicion: -
    // Postcondicion: el codigo ya no esta en el arbol y sigue siendo BST.
    //                Si no existia, el arbol no cambia.
    // Complejidad: O(h)
    // ---------------------------------------------------------------
    void eliminar_aux(Nodo*& nodo, const char* cod) {
        if (nodo == nullptr) return;                  // no existe
        int c = strcmp(cod, nodo->dato.codigo);
        if (c < 0) {
            eliminar_aux(nodo->izq, cod);
        } else if (c > 0) {
            eliminar_aux(nodo->der, cod);
        } else {
            // Lo encontre. Veo cuantos hijos tiene:
            if (nodo->izq == nullptr) {
                // Caso 1 (hoja) y caso 2 (solo hijo derecho):
                // el hijo derecho (o nada) ocupa su lugar
                Nodo* viejo = nodo;
                nodo = nodo->der;
                delete viejo;
                cantidad_--;
            } else if (nodo->der == nullptr) {
                // Caso 2: solo hijo izquierdo, sube ese hijo
                Nodo* viejo = nodo;
                nodo = nodo->izq;
                delete viejo;
                cantidad_--;
            } else {
                // Caso 3: dos hijos. Tomo el sucesor (el menor de la derecha),
                // copio sus datos aqui y borro el sucesor original.
                Nodo* suc = minimo(nodo->der);
                nodo->dato = suc->dato;
                eliminar_aux(nodo->der, nodo->dato.codigo);
            }
        }
    }

    // Libera la memoria (se usa en el destructor). Postorden: hijos primero.
    void liberar_aux(Nodo* nodo) {
        if (nodo == nullptr) return;
        liberar_aux(nodo->izq);
        liberar_aux(nodo->der);
        delete nodo;
    }

public:
    BST_UNAP() : raiz_(nullptr), cantidad_(0) {}
    ~BST_UNAP() { liberar_aux(raiz_); }
    BST_UNAP(const BST_UNAP&) = delete;              // no se copia el arbol
    BST_UNAP& operator=(const BST_UNAP&) = delete;

    void insertar(const Estudiante& e) { insertar_aux(raiz_, e); }

    Estudiante* buscar(const char* cod) {
        Nodo* n = buscar_aux(raiz_, cod);
        return n ? &n->dato : nullptr;
    }

    void eliminar(const char* cod) { eliminar_aux(raiz_, cod); }

    int cantidad() const { return cantidad_; }

    // Llena 'salida' (debe tener espacio para cantidad() elementos)
    // y devuelve cuantos estudiantes guardo.
    int listar_ordenado(Estudiante* salida) const {
        int n = 0;
        inorden_aux(raiz_, salida, n);
        return n;
    }
};

// Revisa que la lista este en orden estricto por codigo
static bool esta_ordenada(const Estudiante* lista, int n) {
    for (int i = 1; i < n; ++i)
        if (strcmp(lista[i - 1].codigo, lista[i].codigo) >= 0) return false;
    return true;
}

// === CASOS DE PRUEBA ===
int main() {
    BST_UNAP arbol;
    arbol.insertar({"UNAP-2023-000050", "Mamani Quispe, Juan",   "Ing. Sistemas"});
    arbol.insertar({"UNAP-2022-000030", "Flores Condori, Ana",   "Ing. Civil"});
    arbol.insertar({"UNAP-2024-000070", "Ticona Apaza, Carlos",  "IACD"});
    arbol.insertar({"UNAP-2021-000020", "Huanca Puma, Lucia",    "Ing. Electrica"});
    arbol.insertar({"UNAP-2023-000040", "Ccopa Ramos, Pedro",    "Ing. Sistemas"});

    Estudiante lista[100];

    // Prueba 1: busqueda exitosa
    Estudiante* e = arbol.buscar("UNAP-2022-000030");
    printf("[P1] %s\n", (e && strcmp(e->nombre, "Flores Condori, Ana") == 0) ? "OK" : "FALLA");

    // Prueba 2: busqueda fallida
    Estudiante* nx = arbol.buscar("UNAP-9999-999999");
    printf("[P2] %s\n", (nx == nullptr) ? "OK" : "FALLA");

    // Prueba 3: listado en orden
    int n = arbol.listar_ordenado(lista);
    printf("[P3] %s\n", (esta_ordenada(lista, n) && n == 5) ? "OK" : "FALLA");

    printf("Listado ordenado:\n");
    for (int i = 0; i < n; ++i)
        printf("  %s - %s\n", lista[i].codigo, lista[i].nombre);

    // Prueba 4: eliminar nodo hoja
    arbol.eliminar("UNAP-2021-000020");
    printf("[P4] %s\n", (arbol.buscar("UNAP-2021-000020") == nullptr) ? "OK" : "FALLA");

    // Prueba 5: eliminar nodo con dos hijos (la raiz)
    arbol.eliminar("UNAP-2023-000050");
    printf("[P5] %s\n", (arbol.buscar("UNAP-2023-000050") == nullptr) ? "OK" : "FALLA");

    // Prueba 6: el arbol sigue siendo un BST valido
    int n2 = arbol.listar_ordenado(lista);
    printf("[P6] %s\n", (esta_ordenada(lista, n2) && n2 == 3) ? "OK" : "FALLA");

    return 0;
}
