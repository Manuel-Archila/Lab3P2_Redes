import slixmpp
from slixmpp.exceptions import IqError, IqTimeout
from slixmpp.xmlstream import ET

#Carcasa del codigo sugerido por Copilot
class Delete_Cliente(slixmpp.ClientXMPP):
    def __init__(self, jid, password):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        self.user = jid
        self.add_event_handler("session_start", self.start)
        
    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        await self.deleteaccount()
        self.disconnect()
        
    
    #Función para eliminar la cuenta    
    async def deleteaccount(self):
        response = self.Iq()
        response['type'] = 'set'
        response['from'] = self.boundjid.user
        fragment = ET.fromstring("<query xmlns='jabber:iq:register'><remove/></query>")
        response.append(fragment)
        
        try:
            await response.send()
            #self.boundjid.jid
            print("\033[92m\nCuenta",self.user,"\033[91mEliminada \033[92mcon exito \033[0m\n")
        except IqError as e:
            print(f"\033[Problemas para enviar la solicitud: {e.iq['error']['text']}\033[0m")
            self.disconnect()
        except IqTimeout:
            print("\033[31mError:\nSe ha excedido el tiempo de respuesta\033[0m")
            self.disconnect()