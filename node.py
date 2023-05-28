import sys
import time as timer
import socket

#leitura de variaveis de inicializacao por parametro
try:
    id = sys.argv[1]
    host = sys.argv[2]
    port = sys.argv[3]
    time = sys.argv[4]
    ptime = sys.argv[5]
    adelay = sys.argv[6]
except IndexError:
    print("ERROR: invalid parameters")
    sys.exit(0)

#Variaveis de controle do tempo de que deve ser chamado calculo mestre
cooldown = 30
berkeley = 0

#sockets de recebimento / envio msgs
send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver = ('', int(port))
recv.bind(receiver)

#leitura de nodos disponiveis
def readNodes(arq):
    return

#timer de cooldown de chamada do algoritmo
def berkeleyCooldown():
    global berkeley
    global cooldown
    while True:
        diff = timer.time() - berkeley
        if diff>cooldown:
            berkeley = timer.time()
            print("Disparando novo calculo")

#calculo feito do algoritmo
def calculo():
    return

#processo mestre sempre sera o com id 0
if id == '0':
    print("Inicializando processo mestre...")
    berkeleyCooldown()
#demais processos
else:
    print("Inicializando nodo...")

