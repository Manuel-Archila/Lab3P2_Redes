from delete_client import Delete_Cliente
import asyncio
abecesario = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]


bandera =1

while bandera < 2:
    
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    bandera =2
    for letra in abecesario:
        user= "archila161250"+ letra.lower() + '@alumchat.xyz'
        d_client = Delete_Cliente(user,user)
        d_client.connect(disable_starttls=True)
        d_client.process(forever=False)
        
    # for letra in abecesario:
    #     user= "Archila161250"+ letra+ '@alumchat.xyz'
    #     d_client = Delete_Cliente(user,letra)
    #     d_client.connect(disable_starttls=True)
    #     d_client.process(forever=False)
    