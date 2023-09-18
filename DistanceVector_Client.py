import slixmpp
from aioconsole import ainput
import asyncio
import time
import ast
import heapq
import datetime

class DistanceVector_Client(slixmpp.ClientXMPP):
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
        self.times = {}
        self.vecinos = []

        self.rutas = {}

        s = self.usu
        pos = s.find('@')
        self.letra_origen = s[pos-1]

        
        self.sigue = True
        self.tiempo = time.time()

        # Se definen los manejadores de eventos
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('message', self.recibir_mensaje)

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

        nodoss = input("Ingrese todos los nodos de la topología separados por coma: ")

        todos_nodos = nodoss.lower()
        todos_nodos = todos_nodos.split(',')


        for nodo in todos_nodos:
            if nodo.lower() == letra_origen:
                self.topologia[nodo.lower()] = 0
            else:
                self.topologia[nodo.lower()] = 10000

            self.rutas[nodo.lower()] = []

            self.times[nodo.lower()] = datetime.datetime.now().timestamp()
            
        
        entrada = input("Ingrese sus vecinos separados por coma: ")
        entrada.lower() 
        nodos = entrada.split(',')
        self.vecinos = nodos
        nodos = [nodo.strip() for nodo in nodos]

        for nodo in nodos:
            node = nodo.lower()
            self.topologia[node.lower()] = 1 

            base = "archila161250"
            jid = base + nodo.lower()
            contacto = f"{jid}"+ "@alumchat.xyz"
            
            await self.add_contact(contacto)
            
        
        await self.sendInfo(letra_origen)

        print(self.topologia)
        
        print("Vecinos agregados correctamente e información enviada a los vecinos.")
        
        while self.sigue:

            if time.time() - self.tiempo > 30:
                self.sigue = False
                break
            
    async def sendInfo(self, origen, paylod = [] ,intermediarios = []):
        palabra_origen = "archila161250" + origen.lower()
        
        if intermediarios == []:
            intermediarios.append(origen)
        
        if paylod == []:
            paylod = self.topologia
            
        paquete = {
            "type": "info", 
            "headers": {
                "origen": palabra_origen, 
                "intermediarios": intermediarios,
                "timestamp": datetime.datetime.now().timestamp()
            },
            "payload": paylod
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

    async def sendmessage(self, to_jid, message, de = " "):

        s = self.usu
        pos = s.find('@')
        letra_origen = s[pos-1]

        if de == " ": 
            de = letra_origen

        letra_destino = to_jid

        
        rutA = self.rutas[letra_destino]

        ruta = rutA.copy()
        
        if len(ruta) == 0:
            siguiente = to_jid
        else:
            siguiente = ruta[0]
            while siguiente == letra_origen:
                ruta.pop(0)
                siguiente = ruta[0]

        
        paquete = {
            "type": "message", 
            "headers": {
                "origen": "archila161250" + de, 
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
            
    async def actualizar_tabla(self, nodo, tabla, tempo):
        nodo = nodo[-1]

        if nodo in self.times:
            if tempo <= self.times[nodo]:
                return
        
        self.times[nodo] = tempo

        for key in tabla:
            if key != self.letra_origen:
                # Considere la distancia de la tabla recibida más la distancia al nodo del que recibió la información
                val = tabla[key] + self.topologia[nodo]
                # Actualice la distancia solo si es menor que la conocida
                if val < self.topologia[key]:
                    self.rutas[key].append(nodo)
                    self.topologia[key] = val


        
        print(f"Actualización de tabla recibida de .{nodo}")
        print(self.topologia)

    async def recibir_mensaje(self, msg):
        # Se verifica si el mensaje es de tipo chat o normal
        if msg['type'] in ('chat', 'normal'):

            objeto = ast.literal_eval(msg['body'])

            if objeto['type'] == "info":

                self.tiempo = time.time()   
                origen = objeto['headers']['origen']
                intermediarios = objeto['headers']['intermediarios']
                try:
                    tempo = objeto['headers']['timestamp']
                except:
                    fecha_hora_actual = datetime.datetime.now()
                    tempo = fecha_hora_actual.timestamp()
                
                payload = objeto['payload']

                s = self.usu
                pos = s.find('@')
                letra_origen = s[pos-1]

                if letra_origen in intermediarios:
                    return

                intermediarios.append(letra_origen)

                await self.actualizar_tabla(origen, payload, tempo)
                
                
                await self.sendInfo(origen[-1], payload, intermediarios)
            
            else:
                
                s = self.usu
                pos = s.find('@')
                actual = s[pos-1]

                if objeto['headers']['destino'][-1] == actual:
                    print(f"El mensaje de {objeto['headers']['origen']} ha llegado correctamente.")
                    print(objeto['payload'])
                    print("*****************************************************")
                    
                else:

                    origen = objeto['headers']['origen'][-1]

                    destino = objeto['headers']['destino'][-1]
                    

                    rutA = self.rutas[destino]

                    ruta = rutA.copy()
        
                    if len(ruta) == 0:
                        siguiente = destino
                    else:
                        siguiente = ruta[0]
                        while siguiente == origen:
                            ruta.pop(0)
                            siguiente = ruta[0]
            
                    
                    print(f"Mensaje de {origen} hacia {destino} recibido y reenviado.")

                    await self.sendmessage(siguiente, objeto['payload'], origen)
    
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
                    
                    jid = letra.lower()

                    message = input("Ingrese el mensaje que desea enviar: ")

                    print(self.rutas)

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
    
    
