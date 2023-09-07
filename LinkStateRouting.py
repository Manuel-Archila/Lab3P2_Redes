from nodo import *
import heapq

class LinkStateRouting():
    def __init__(self):
        self.topologia = {}
    
    def enviar_topologia(self, nodo):
        return nodo.distancias  # Cambio aquí

    def recibir_topologia(self, nodo, mensaje):
        self.topologia[nodo.nombre].distancias = mensaje  # Cambio aquí

    def agregar_nodo(self, nodo):
        self.topologia[nodo.nombre] = nodo

    def calcular_info(self, nodo):
        for key in nodo.distancias:  # Cambio aquí
            print(key)

    def calcular_ruta(self, origen, destino):
        distancias = {nodo: float('inf') for nodo in self.topologia}
        predecesores = {nodo: None for nodo in self.topologia}  # Diccionario de predecesores
        distancias[origen] = 0
        nodos_pendientes = [(0, origen)]
        visitados = set()

        while nodos_pendientes:
            distancia_actual, nodo_actual = heapq.heappop(nodos_pendientes)
            if nodo_actual in visitados:
                continue
            visitados.add(nodo_actual)

            for vecino, distancia in self.topologia[nodo_actual].distancias.items():
                nueva_distancia = distancia_actual + distancia
                if nueva_distancia < distancias[vecino]:
                    distancias[vecino] = nueva_distancia
                    predecesores[vecino] = nodo_actual  # Actualizar el predecesor para este vecino
                    heapq.heappush(nodos_pendientes, (nueva_distancia, vecino))

        # Reconstruir el camino desde el destino al origen usando el diccionario de predecesores
        camino = []
        nodo_actual = destino
        while nodo_actual is not None:
            camino.insert(0, nodo_actual)  # Agregar al inicio para reconstruir en el orden correcto
            nodo_actual = predecesores[nodo_actual]

        return camino
    
    def ver_topologia(self):
        for nodo, detalles in self.topologia.items():
            print(f"{nodo}: {detalles.distancias}")  # Cambio aquí

    def enviar_mensaje(self, tipo, saltos, origen, mensaje, destino, intermediario):
        
        origen_ = None
        if type(origen).__name__ == "Nodo":
            origen_ = origen.nombre
        else:
            origen_ = origen
            origen = intermediario.nombre

        

        camino = self.calcular_ruta(origen, destino)
        next = camino[1]

        print("\n Enviar este paquete a :", next)

        paquete = {
            "type": tipo, 
            "headers": {
                "from": origen_, 
                "to": destino,
                "hop_count": saltos
            }, 
            "payload": mensaje
        }

        print(paquete)

    def recibir_mensaje(self, emisor, receptor, mensaje, tipo, saltos, actual):
        if receptor == actual.nombre:
            print("Mensaje recibido: ", mensaje)
            return
    
        if saltos == 0:
            print("Mensaje perdido")
            return
        
        saltos -= 1
        self.enviar_mensaje(tipo, saltos, emisor, mensaje, receptor, actual)