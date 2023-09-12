import xmpp

from Flooding_Client import Flooding_Client
from LinkState_Cliente import LinkState_Client
from DistanceVector_Client import DistanceVector_Client

def register(client, password):
        jid = xmpp.JID(client)
        account = xmpp.Client(jid.getDomain(), debug=[])
        account.connect()
        return bool(
            xmpp.features.register(account, jid.getDomain(), {
                'username': jid.getNode(),
                'password': password
    }))


def iniciar_sesionF(jid, password):

    # Creamos un objeto cliente
    xmpp = Flooding_Client(jid, password)

    # Nos conectamos al servidor
    xmpp.connect(disable_starttls=True)
    xmpp.process(forever=False)


def iniciar_sesionL(jid, password):

    # Creamos un objeto cliente
    xmpp = LinkState_Client(jid, password)

    # Nos conectamos al servidor
    xmpp.connect(disable_starttls=True)
    xmpp.process(forever=False)


def iniciar_sesionV(jid, password):

    # Creamos un objeto cliente
    xmpp = DistanceVector_Client(jid, password)

    # Nos conectamos al servidor
    xmpp.connect(disable_starttls=True)
    xmpp.process(forever=False)