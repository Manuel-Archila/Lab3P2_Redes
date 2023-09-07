import ast

class Router:
    def __init__(self, name, neighbors, total_vecinos):
        self.name = name
        self.todos_vecinos = total_vecinos
        self.neighbors = neighbors

        self.diccionario_principal = {
            nombre: [[vecino, self.neighbors.get(vecino, 0)] for vecino in self.todos_vecinos]
        }

        self.getCamino()

    def getCamino(self):
        self.camino = {}
        for nodo in self.diccionario_principal:
            for vecino in self.diccionario_principal[nodo]:
                if vecino[0] != nodo and vecino[0] not in self.neighbors.keys():
                    self.camino[vecino[0]] = ""
                    
    def actualizar_ruta(self, diccionario_vecino):
        nodo1 = self.name
        nodo2 = list(diccionario_vecino.keys())[0]  # Suponemos que diccionario_vecino solo tiene una entrada

        # Obtener la distancia de nodo1 a nodo2
        distancia_nodo1_a_nodo2 = next((v[1] for v in self.diccionario_principal[nodo1] if v[0] == nodo2), 0)

        # Si no hay conexión, entonces no actualizamos
        if distancia_nodo1_a_nodo2 == 0:
            print("No hubo cambios en las rutas")
            return

        actualizados = False

        for vecino in diccionario_vecino[nodo2]:
            nombre_vecino, distancia_nodo2_a_vecino = vecino

            # Si el vecino es el mismo nodo o no hay conexión directa con el vecino, continuamos sin hacer nada
            if nombre_vecino == nodo1 or distancia_nodo2_a_vecino == 0:
                continue

            distancia_total = distancia_nodo1_a_nodo2 + distancia_nodo2_a_vecino

            # Obtener la distancia actual desde nodo1 al nombre_vecino
            distancia_actual_a_vecino = next((v[1] for v in self.diccionario_principal[nodo1] if v[0] == nombre_vecino), 0)

            # Si la distancia total es menor a la distancia actual registrada, o si no hay una ruta existente (distancia 0), actualizamos
            if (distancia_actual_a_vecino == 0) or (distancia_total < distancia_actual_a_vecino):
                for v in self.diccionario_principal[nodo1]:
                    if v[0] == nombre_vecino:
                        v[1] = distancia_total
                        actualizados = True
                        self.camino[nombre_vecino] = nodo2
                        break
                else:
                    # Si el nodo vecino no estaba en el diccionario del nodo1, lo añadimos
                    self.diccionario_principal[nodo1].append([nombre_vecino, distancia_total])
                    actualizados = True
                    self.camino[nombre_vecino] = nodo2

        if not actualizados:
            print("No hubo cambios en las rutas")

    def imprimir_tabla(self):
        print(self.camino)

        print("=" * 30)

        print(f'Nombre: {self.name}')
        print('Vecino | Valor')
        print('----------------')
        
        for vecino, valor in self.diccionario_principal[self.name]:
            print(f'{vecino:^7} | {valor:^5}')

        print(self.diccionario_principal)

        print("=" * 30)

    def enviar_mensaje(self, tipo, saltos, origen, mensaje, destino):
        enviado = True

        while enviado :

            if destino in self.neighbors.keys():
                enviado = False

                print("Enviar este paquete a :", destino)

                paquete = {
                    "type": tipo, 
                    "headers": {
                        "from": origen, 
                        "to": destino,
                        "hop_count": saltos
                    }, 
                    "payload": mensaje
                }

                print(paquete)

            else:
                destino = self.camino[destino]

    def recibir_mensaje(self, receptor, mensaje, tipo, saltos, emisor):
        if saltos > 0 and receptor != self.name:
           saltos = saltos - 1

           self.enviar_mensaje(tipo, saltos, emisor, mensaje, receptor)

            
        else:
            print("\nMensaje recibido")
            print(mensaje)