# Importamos las clases que vamos a utilizar
from Flooding_Client import Flooding_Client
import xmpp
import slixmpp
import asyncio

from utils import *


print("Bienvenido al cliente de mensajería XMPP")
# Configuramos el bucle de eventos
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

while True:
    # Mostramos el menú de opciones
    print("(1) Flooding\n(2) LinkState\n(3) DistanceVector\n")
    choice = input("¿Que algoritmo deseas utilizar?: ")

    # Dependiendo de la opción elegida, se ejecuta una acción

    if choice == "1":
        print("Has elegido Flooding")

        print("Introduce tus credenciales de usuario para el uso del cliente XMPP")

        base = "archila161250"
        letra = input("Ingrese la letra del nuevo nodo: ")

        jid = base + letra.lower()

        password = jid

        jid = f"{jid}@alumchat.xyz"


        if register(jid, password) :
            print("¡Cuenta creada exitosamente!")
        else:
            print("Error al crear la cuenta. Por favor, intente nuevamente.")
            break

        iniciar_sesion(jid, password)


    elif choice == "2":
        print("Has elegido LinkState")

        print("Introduce tus credenciales de usuario para el uso del cliente XMPP")

    elif choice == "3":
        print("Has elegido DistanceVector")

        print("Introduce tus credenciales de usuario para el uso del cliente XMPP")


    else:
        print("Opción inválida. Por favor, elige '1' o '2' o '3'.")
