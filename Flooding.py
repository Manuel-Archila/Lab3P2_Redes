class Flooding(object):
    def __init__(self):
        pass

    def enviar_mensaje(self, tipo, saltos, origen, mensaje, destino, intermediario, intermediarios = []):
        temp = ""
        bandera = False

        if type(origen).__name__ == "Nodo":
            temp = origen.nombre
        
        else:
            temp = origen
            origen = intermediario
            bandera = True

        if origen.nombre not in intermediarios:
            intermediarios.append(origen.nombre)


        if temp == destino:
            return mensaje
        
        else:

            for vecino in origen.vecinos:

                if vecino in intermediarios:
                    continue
                
                if bandera:
                    if vecino != temp:
                        print("\n Enviar este paquete a :", vecino)
                        print()
                        
                        paquete = {
                            "type": tipo, 
                            "headers": {
                                "from": temp, 
                                "to": destino,
                                "hop_count": saltos,
                                "intermediarios": ",".join(intermediarios)
                            }, 
                            "payload": mensaje
                        }

                        print(paquete)
                        
                    else:
                        pass
                else:

                    if vecino != origen.nombre:
                        print("\n Enviar este paquete a :", vecino)
                        print()
                        
                        paquete = {
                            "type": tipo, 
                            "headers": {
                                "from": temp, 
                                "to": destino,
                                "hop_count": saltos,
                                "intermediarios": ",".join(intermediarios)
                            }, 
                            "payload": mensaje
                        }

                        print(paquete)
                    else:
                        pass

    def recibir_mensaje(self, actual, receptor, mensaje, tipo, saltos, emisor, intermediarios):
        if saltos > 0 and receptor != actual.nombre:

            intermediarios.append(actual.nombre)
            saltos -= 1
            for vecino in actual.vecinos:

                if vecino not in intermediarios:
                    self.enviar_mensaje(tipo, saltos, emisor, mensaje, receptor, actual, intermediarios)
                    print()
        else:
            print("\nMensaje recibido")
            print(mensaje)
