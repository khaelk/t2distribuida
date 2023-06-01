import sys
import socket
from time import sleep
import datetime

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
    for node in ipPortas:
        print("Enviando ordem de envio de tempo SENDTIME para o nodo de IP:PORTA", node)
        send.sendto(bytes("SENDTIME;", "utf8"), (node.split(":")[0], int(node.split(":")[1]))) # ajustar para enviar para todos nodos
        #adicionar timeout de finalizar programa aqui caso nao receba em certo tempo
        recvPacket, client = recv.recvfrom(1024)
        print(recvPacket, client)
    
    #apos envio receber
    #comunicacao (sends) feita 2 vezes quando peco o tempo
    #(aqui no meio fica o calculo aritmetico)
    #e quando atualizo o tempo
    #finaliza enviando os tempos atualizados

#processo mestre sempre sera o com id 0
if id == '0':
    print("Inicializando processo mestre...")
    #quando inicializa o mestre settar nodos
    ipPortas = readNodes("nodes.txt")
    print("Lista de IPs e portas dos nodos: ",ipPortas)
    while True:
        calculo(ipPortas)
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
        print("Ordem recebida: ", recvPacket, client)
        if recvPacket.split(";")[0] == "SENDTIME":
            #envio o meu tempo
            time = 0
            print("Executando ordem de envio de tempo")
            send.sendto(bytes("bnana", "utf8"), (str(client[0]), 1024))
        elif recvPacket.split(";")[0] == "UPDATETIME":
            #atualizo o o tempo
            time = 0
            print("Executando ordem de atualizacao de tempo")

