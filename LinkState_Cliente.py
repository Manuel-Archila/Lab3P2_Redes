import slixmpp
from aioconsole import ainput
import asyncio
import time
import ast
import heapq

class LinkState_Client(slixmpp.ClientXMPP):
    # Definimos el constructor de la clase
    def __init__(self, jid, password):

        # Llamamos al constructor de la clase padre
        super().__init__(jid, password)

        # Se definene los atributos de la clase
        self.conectado = False
        self.usu = jid.lower()
        self.primera = True
        self.cont = []
        self.estados = []
        self.mensajes_recibidos = {}
        self.topologia = {}

        
        self.sigue = True
        self.tiempo = time.time()

        # Se definen los manejadores de eventos
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('message', self.recibir_mensaje)
        #self.add_event_handler('groupchat_invite', self.aceptGroup)
        #self.add_event_handler('changed_status', self.presence_handler)

        # Se registran los plugins
        self.register_plugin('xep_0045')
        self.register_plugin('xep_0004')

    async def start(self, event):
        # Se obtiene el roster al iniciar la sesion
        self.send_presence()
        self.get_roster()
        self.conectado = True
        print("Sesión iniciada correctamente. \n")
        await self.get_roster()
        await self.show_contacts()
        await self.obtener_vecinos()

        asyncio.create_task(self.interactuar_con_cliente())

    async def obtener_vecinos(self):
        s = self.usu
        pos = s.find('@')
        letra_origen = s[pos-1]
        
        entrada = input("Ingrese sus vecinos separados por coma: ")
        entrada.lower() 
        nodos = entrada.split(',')
        nodos = [nodo.strip() for nodo in nodos]
        self.topologia[letra_origen] = {}

        for nodo in nodos:
            self.topologia[letra_origen][nodo] = 1 

            base = "archila161250"
            jid = base + nodo.lower()
            contacto = f"{jid}"+ "@alumchat.xyz"
            
            await self.add_contact(contacto)
            
        
        await self.sendInfo(letra_origen, nodos)
        
        print("Vecinos agregados correctamente e información enviada a los vecinos.")
        
        while self.sigue:

            if time.time() - self.tiempo > 45:
                self.sigue = False
                break
            
    async def sendInfo(self, origen, vecinos, intermediarios = []):
        palabra_origen = "archila161250" + origen.lower()

        if intermediarios == []:
            intermediarios.append(origen)
            
        paquete = {
            "type": "info", 
            "headers": {
                "origen": palabra_origen, 
                "intermediarios": intermediarios,
            },
            "payload": vecinos
        }
        paquete_string = str(paquete)

        try:
            roster = self.client_roster
            contacts = roster.keys()
            
            for usuario in contacts:
                if usuario != self.usu:
                    self.send_message(mto=usuario, mbody=paquete_string, mtype='chat')
        except:
            print("Error al enviar el mensaje.")
        
    async def show_contacts(self):
        # Se obtiene el roster y sus keys
        roster = self.client_roster
        contacts = roster.keys()
        contactos = []

        # Se recorren los contactos para saber si si hay o no
        if not contacts and not self.primera:
            print("El nodo no tiene vecionos.")
            return
        
        # Se recorren los contactos para obtener su estado
        for jid in contacts:
            user = jid

            if '@conference' in user:
                continue

            connection = roster.presence(jid)
            show = 'Desconectado'
            status = ''
            if user != self.usu:
                for answer, presence in connection.items():
                    if presence:
                        show = presence['show']
                    if presence['status']:
                        status = presence['status']

                    # Se hace la codificacion de los estados
                    if show == 'dnd':
                        show = 'Ocupado'
                    if show == 'xa':
                        show = 'No disponible'
                    if show == 'away':
                        show = 'Ausente'
                    if show == '':
                        show = 'Disponible'
                if self.primera:
                    self.cont.append(user)
                    self.estados.append((user, show))
                contactos.append((user, show, status))
        
        # Se muestran los contactos
        if not self.primera:
            print("\nLos vecinos del nodo son: \n")
            for c in contactos:
                print(f"Contacto: {c[0]}")
                print(f"Estado: {c[1]}")
                print(f"Mensaje de estado: {c[2]}")
                print("")
            print("")
        self.primera = False

    async def add_contact(self, jid):
        # Se envia la solicitud de suscripcion
        self.send_presence_subscription(pto=jid)
        await self.get_roster()
        print("Contacto agregado correctamente.")

    async def sendmessage(self, to_jid, message):

        s = self.usu
        pos = s.find('@')
        letra_origen = s[pos-1]


        s = to_jid
        pos = s.find('@')
        letra_destino = s[pos-1]

        
        ruta = self.calcular_ruta(letra_origen, letra_destino)
        siguiente = ruta[0]
        while siguiente == letra_origen:
            ruta.pop(0)
            siguiente = ruta[0]

        print(f"La ruta es: {ruta}")
        
        paquete = {
            "type": "message", 
            "headers": {
                "origen": "archila161250" + letra_origen, 
                "destino": "archila161250" + letra_destino
            },
            "payload": message
        }
        paquete_string = str(paquete)

        try:
            roster = self.client_roster
            contacts = roster.keys()
            
            for usuario in contacts:
                letra = usuario.find('@')
                letra = usuario[letra-1]
                
                if letra == siguiente:
                    self.send_message(mto=usuario, mbody=paquete_string, mtype='chat')

        except:
            print("Error al enviar el mensaje.")

    async def recibir_mensaje(self, msg):
        # Se verifica si el mensaje es de tipo chat o normal
        if msg['type'] in ('chat', 'normal'):

            objeto = ast.literal_eval(msg['body'])

            if objeto['type'] == "info":

                self.tiempo = time.time()   
                origen = objeto['headers']['origen']
                intermediarios = objeto['headers']['intermediarios']
                
                s = self.usu
                pos = s.find('@')
                letra_origen = s[pos-1]

                if letra_origen in intermediarios:
                    return

                payload = objeto['payload']

                origen = origen[-1]
                
                self.topologia[origen] = {}
                for nodo in payload:
                    self.topologia[origen][nodo] = 1
                

                intermediarios.append(letra_origen)
                
                await self.sendInfo(origen, payload, intermediarios) 
            
            else:
                
                s = self.usu
                pos = s.find('@')
                actual = s[pos-1]

                if objeto['headers']['destino'] == actual:
                    print(f"El mensaje de {objeto['headers']['origen']} ha llegado correctamente.")
                    print(objeto['payload'])
                    print("*****************************************************")
                    
                else:

                    origen = objeto['headers']['origen']

                    destino = objeto['headers']['destino']
                    

                    ruta = self.calcular_ruta(actual, destino)
                    siguiente = ruta[0]
                    while siguiente == actual:
                        ruta.pop(0)
                        siguiente = ruta[0]
            
                    
                    print(f"Mensaje de {origen} hacia {destino} recibido y reenviado a vecinos.")
                    try:
                        roster = self.client_roster
                        contacts = roster.keys()
                        
                        for usuario in contacts:
                            letra = usuario.find('@')
                            letra = usuario[letra-1]

                            if letra == siguiente:
                                self.send_message(mto=usuario, mbody=msg['body'], mtype='chat')
                                
                    except:
                        print("Error al enviar el mensaje.")
    
    def calcular_ruta(self, origen, destino):
        # Inicializar distancias y predecesores
        distancias = {nodo: float('infinity') for nodo in self.topologia}
        predecesores = {nodo: None for nodo in self.topologia}
        distancias[origen] = 0
        
        nodos_no_visitados = list(self.topologia.keys())
        
        while nodos_no_visitados:
            # Seleccionar el nodo con la distancia más corta
            nodo_actual = min(nodos_no_visitados, key=lambda nodo: distancias[nodo])
            
            if distancias[nodo_actual] == float('infinity'):
                break
            
            # Si hemos llegado al destino, terminamos
            if nodo_actual == destino:
                break
            
            # Actualizar distancias de los nodos vecinos
            for vecino, distancia in self.topologia[nodo_actual].items():
                if distancia > 0:  # Verificar que son vecinos
                    nueva_distancia = distancias[nodo_actual] + distancia
                    if nueva_distancia < distancias[vecino]:
                        distancias[vecino] = nueva_distancia
                        predecesores[vecino] = nodo_actual
            
            nodos_no_visitados.remove(nodo_actual)
        
        # Reconstruir la ruta desde el destino hasta el origen
        ruta = []
        nodo_actual = destino
        while nodo_actual:
            ruta.insert(0, nodo_actual)
            nodo_actual = predecesores[nodo_actual]
        
        return ruta
    
    def eliminar_cuenta(self):
        delete_stanza = f""" 
                <iq type="set" id="delete-account">
                <query xmlns="jabber:iq:register">
                    <remove jid="{self.username}"/>
                </query>
                </iq>
            """

        print(self.send_raw(delete_stanza))    

    async def interactuar_con_cliente(self):

        while self.conectado:
            try:
                # Se muestra el menu de opciones
                print("*****************************************************")
                print("Menú de opciones:")
                print("1) Mostrar topologia.")
                print("2) Enviar un mensaje.")
                print("3) Salir.")
                print("*****************************************************\n")

                # Se obtiene la opcion elegida
                opcion = await ainput("Ingrese el número de la opción deseada: \n")

                if opcion == "1":
                    #await self.show_contacts()
                    print(self.topologia)

                elif opcion == "2":
                    letra = input("Ingrese el nombre del vecino al que desea enviar el mensaje: ")
                    base = "archila161250"
                    jid = base + letra.lower()
                    jid = f"{jid}@alumchat.xyz"

                    message = input("Ingrese el mensaje que desea enviar: ")

                    await self.sendmessage(jid, message)

                    

                elif opcion == "3":
                    # eliminar cuenta
                    self.eliminar_cuenta()
                    self.disconnect()
                    self.conectado = False

                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")
            except Exception as e:
                print(f"Error: {e}")
    
    
