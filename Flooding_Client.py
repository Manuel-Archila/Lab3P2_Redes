import slixmpp
from aioconsole import ainput
import asyncio
import time
import ast
import base64
import datetime


class Flooding_Client(slixmpp.ClientXMPP):
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

        asyncio.create_task(self.interactuar_con_cliente())

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

        origen_temp = self.usu.split('@')[0]
        destino_temp = to_jid.split('@')[0]

        paquete = {
            "type": "message", 
            "headers": {
                "origen": origen_temp, 
                "destino": destino_temp,
                "intermediarios": [origen_temp],
                "timestamp": datetime.datetime.now().timestamp()
            },
            "payload": message
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

    async def resendmessage(self, to_jid, message, intermediarios, origen):
        actual = self.usu.split('@')[0]
        
        intermediarios.append(actual)
        paquete = {
            "type": "message", 
            "headers": {
                "origen": origen, 
                "destino": to_jid,
                "intermediarios": intermediarios,
                "timestamp": datetime.datetime.now().timestamp()
            },
            "payload": message
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

    async def recibir_mensaje(self, msg):
        # Se verifica si el mensaje es de tipo chat o normal
        if msg['type'] in ('chat', 'normal'):

            objeto = ast.literal_eval(msg['body'])

            for key, item in self.mensajes_recibidos.items():
                if item >= objeto['headers']['timestamp'] and key == objeto['headers']['origen']:
                    return
            
            self.mensajes_recibidos[objeto['headers']['origen']] = objeto['headers']['timestamp']

            actual = self.usu.split('@')[0]
            if objeto['headers']['destino'] == actual:
                print(f"El mensaje de {objeto['headers']['origen']} ha llegado correctamente.")
                print(objeto['payload'])
                print("*****************************************************")
                
            else:
                origen = objeto['headers']['origen']
                

                destino = objeto['headers']['destino']
                
                print(f"Mensaje de {origen} hacia {destino} recibido y reenviado a vecinos.")
                try:
                    roster = self.client_roster
                    contacts = roster.keys()
                    
                    for usuario in contacts:
                        if usuario != self.usu and actual not in objeto['headers']['intermediarios']:
                            await self.resendmessage(objeto['headers']['destino'], objeto['payload'], objeto['headers']['intermediarios'], objeto['headers']['origen'])
                except:
                    print("Error al enviar el mensaje.")

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
                print("1) Mostrar vecinos.")
                print("2) Agregar vecinos del nodo.")
                print("3) Enviar un mensaje.")
                print("4) Salir.")
                print("*****************************************************\n")

                # Se obtiene la opcion elegida
                opcion = await ainput("Ingrese el número de la opción deseada: \n")

                if opcion == "1":
                    await self.show_contacts()

                elif opcion == '2':
                    # Se obtiene el JID del usuario a agregar y se agrega haciendo uso de la funcion add_contact
                    add_vecinos = True
                    vecinos = []
                    while add_vecinos:
                        letra = input("Ingrese el nombre del vecino que desea agregar: ")
                        base = "archila161250"
                        jid = base + letra.lower()
                        jid = f"{jid}@alumchat.xyz"
                        vecinos.append(jid)

                        mas = input("¿Desea agregar otro vecino? (s/n): ")
                        
                        if mas == 'n':
                            add_vecinos = False
                    
                    for jid in vecinos:
                        await self.add_contact(jid)
                    
                    print("Vecinos añadidos correctamente")

                elif opcion == '3':
                    letra = input("Ingrese el nombre del vecino al que desea enviar el mensaje: ")
                    base = "archila161250"
                    jid = base + letra.lower()
                    jid = f"{jid}@alumchat.xyz"

                    message = input("Ingrese el mensaje que desea enviar: ")

                    await self.sendmessage(jid, message)

                elif opcion == '4':
                    # eliminar cuenta
                    self.eliminar_cuenta()
                    self.disconnect()
                    self.conectado = False

                else:
                    print("Opción inválida. Por favor, ingrese un número válido.")
            except Exception as e:
                print(f"Error: {e}")
    
    
