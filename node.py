import sys
import socket
import time
from time import sleep
import datetime

#leitura de variaveis de inicializacao por parametro
try:
    id = sys.argv[1]
    host = sys.argv[2]
    port = sys.argv[3]
    timeSt = sys.argv[4]
    ptime = sys.argv[5]
    adelay = sys.argv[6]
except IndexError:
    print("ERROR: invalid parameters")
    sys.exit(0)

#Variaveis de controle do tempo de que deve ser chamado calculo mestre
cooldown = 30
berkeley = 0

ct = datetime.datetime.now()
print(ct)
ts = ct.timestamp()
print(ts)

#sockets de recebimento / envio msgs
send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver = ('', int(port))
recv.bind(receiver)

#leitura de nodos disponiveis
def readNodes(arq):
    ipPortas = []
    with open(arq, 'r') as f:
        for line in f:
            ipPortas.append(line.rstrip("\n"))
    return ipPortas

#calculo feito do algoritmo
def calculo(ipPortas):
    print("Enviando mensagem para todos nodos, ordem: SENDTIME")
    times = []
    times.append(timeSt)
    for node in ipPortas:
        print("Enviando ordem de envio de tempo SENDTIME para o nodo de IP:PORTA", node)
        send.sendto(bytes("SENDTIME;", "utf8"), (node.split(":")[0], int(node.split(":")[1]))) # ajustar para enviar para todos nodos
        #adicionar timeout de finalizar programa aqui caso nao receba em certo tempo
        try:
            recvPacket, client = recv.recvfrom(1024)
        except Exception as e:
            print("Erro no recebimento do tempo de um nodo!")
            exit()
        print("TIME:",int(recvPacket), client)
        times.append(str(recvPacket))
    tList = times.copy()
    #(aqui fica o calculo aritmetico usando tList)
    #while flag != true
    #   media de valores em times
    #   check se ninguem distoa > 10s se distoa removo da lista e chama media de novo
    #   se ninguem distoa seto flag == false
    #   
    #com a media calculo tp1 = avg - times[tp1] + rtt/2
    #lista times order == nodes.txt order, logo for node in ipPortas...
    #send atualizacao do tempo (qual tempo deve ser imposto aos nodos)

#processo mestre sempre sera o com id 0
if id == '0':
    print("Inicializando processo mestre...")
    #quando inicializa o mestre settar nodos
    ipPortas = readNodes("nodes.txt")
    #set timeout para recebimento de tempo dos nodos
    recv.settimeout(10)
    print("Lista de IPs e portas dos nodos cadastrados em nodos.txt: ",ipPortas)
    while True:
        calculo(ipPortas)
        #sleep de cooldown para executar o algoritmo novamente
        sleep(cooldown)
#demais processos
else:
    print("Inicializando nodo...")
    while True:
        print("Esperando recebimento de ordem")
        #packet -> msg str com comandos
        #client -> (ip do client, porta que enviou)
        packet, client = recv.recvfrom(int(port))
        recvPacket = str(packet, "utf8")
        print("Ordem recebida: ", recvPacket, client)
        if recvPacket.split(";")[0] == "SENDTIME":
            #envio o meu tempo
            time = 0
            print("Executando ordem de envio de tempo")
            #count time here
            send.sendto(bytes(str(time), "utf8"), (str(client[0]), 1024))
        elif recvPacket.split(";")[0] == "UPDATETIME":
            #atualizo o o tempo
            print("Executando ordem de atualizacao de tempo para", recvPacket.split(";")[1])
            time = recvPacket.split(";")[1]
            print("Meu novo tempo: ", time)

