import sys
import time as timer
import socket
import threading
from time import sleep

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

#calculo feito do algoritmo
def calculo():
    send.sendto(bytes("SENDTIME;", "utf8"), ('127.0.0.1', 1025)) # ajustar para enviar para todos nodos
    #apos envio receber
    #comunicacao (sends) feita 2 vezes quando peco o tempo
    #(aqui no meio fica o calculo aritmetico)
    #e quando atualizo o tempo
    #finaliza enviando os tempos atualizados

#processo mestre sempre sera o com id 0
if id == '0':
    print("Inicializando processo mestre...")
    #quando inicializa o mestre realizar reconhecimento
    while True:
        calculo()

        #sleep de cooldown para executar o algoritmo novamente
        sleep(cooldown)
#demais processos
else:
    print("Inicializando nodo...")
    while True:
        print("Esperando recebimento de ordem")
        #packet -> msg str com operacao a ser feita
        #client -> (ip do client, porta que enviou)
        packet, client = recv.recvfrom(int(port))
        recvPacket = str(packet, "utf8")
        print(recvPacket, client)

