import sys
import socket
from time import sleep
import datetime
import time
import threading
import os

# Leitura de parametros de inicializacao
try:
    id = sys.argv[1]
    host = sys.argv[2]
    port = sys.argv[3]
    inputs = sys.argv[4].split(":")
    #100,1,1 dummy date for years months days
    myTime = datetime.datetime(2000,1,1, int(inputs[0]), int(inputs[1]), 0) + datetime.timedelta(seconds=float(inputs[2]))
    ptime = float(sys.argv[5])
    adelay = float(sys.argv[6])
except IndexError:
    print("ERROR: invalid parameters")
    sys.exit(0)

# Variaveis de controle do tempo de que deve ser chamado calculo mestre
cooldown = 30
berkeley = 0

mean_diff = 10

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

def clocker():
    global myTime
    while True:
        sleep(1)
        myTime = datetime.datetime.fromtimestamp(datetime.datetime.timestamp(myTime) + 1)
        print(myTime.time())

#calculo feito do algoritmo
def calculo(ipPortas):
    global myTime
    print("Enviando mensagem para todos nodos, ordem: SENDTIME")
    times = []
    tList = []
    deltas = []
    rtts = []
    for node in ipPortas:
        print("Enviando ordem de envio de tempo SENDTIME para o nodo de IP:PORTA", node)
        send.sendto(bytes("SENDTIME", "utf8"), (node.split(":")[0], int(node.split(":")[1]))) # ajustar para enviar para todos nodos
        t1 = datetime.datetime.timestamp(myTime)
        try:
            recvPacket, client = recv.recvfrom(1024)
        except Exception as e:
            print("Erro no recebimento do tempo de um nodo!")
            os._exit(1)
        t4 = datetime.datetime.timestamp(myTime)
        rtt = t4 - t1
        #transforma msg em bytes recebida em datetime obj
        date_str = recvPacket.decode()
        date_ts = float(date_str)
        print("Time recebido:", datetime.datetime.fromtimestamp(date_ts).time(), client)
        #diferença do meu tempo atual ao horario recebido
        delta = datetime.datetime.timestamp(myTime) - date_ts
        print(f'{datetime.datetime.timestamp(myTime)} - {date_ts}')
        print("Delta:", delta, "s")
        deltas.append(delta)
        rtts.append(rtt)
    tList.append(datetime.datetime.timestamp(myTime))
    for d in deltas:
        times.append(datetime.datetime.timestamp(myTime) - d)
        tList.append(datetime.datetime.timestamp(myTime) - d)
    avg = 0
    n = 1
    flag = False
    #(aqui fica o calculo aritmetico usando tList)
    while flag != True:
        print("Iniciando calculo de media.")
    #   caso todos distoem o avg vira myTime (master time)
        if len(tList) == 0:
            print("Tempos muito distoantes setto o meu tempo.")
            avg = datetime.datetime.timestamp(myTime)
            print("AVG", n, ":", avg)
            break
    #   media de valores em timestamp
        avg = (sum(tList)) / len(tList)
        print(f'sum{tList} / {len(tList)}')
    #   se ninguem distoa seto flag == True finalizando calc media
        flag = True
        print("AVG", n, ":", avg)
        n = n+1
    #   check se ninguem distoa > 10s se distoa removo da lista e chama media de novo
        tAux = []
        tAux[:] = [x for x in tList if abs(x-avg)<=mean_diff]
        print(tList, tAux)
        if len(tAux) != len(tList):
            tList = tAux
            flag = False

    print("Media final calculada:", avg)
    newTime = datetime.datetime.timestamp(myTime) + (avg - float(datetime.datetime.timestamp(myTime)))
    print("Devo adiantar meu tempo em:", (avg - float(datetime.datetime.timestamp(myTime))), "s")
    myTime = datetime.datetime.fromtimestamp(newTime)
    print("Atualizei meu tempo para:", myTime.time())
    print("Enviando mensagem para todos nodos, ordem: UPDATETIME")
    #ajustar for para percorrer 2 listas -> tempos atualizados e de nodos
    index = 0
    for node in ipPortas:
        #com a media calculo tp1 = avg - times[tp1] + rtt/2
        newT = avg - times[index] + rtts[index]/2 # + RTT
        print("Enviando ordem de atualizacao de tempo para o nodo de IP:PORTA", node, "em", newT, "s")
        newT = str(newT)
        send.sendto(newT.encode(), (node.split(":")[0], int(node.split(":")[1])))
        index = index + 1

#processo mestre sempre sera o com id 0
if id == '0':
    print("Inicializando processo mestre...", myTime.time())
    threading.Thread(target=clocker).start()
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
    print("Inicializando nodo...", myTime.time())
    threading.Thread(target=clocker).start()
    while True:
        print("Esperando recebimento de ordem")
        #packet -> msg str com comandos
        #client -> (ip do client, porta que enviou)
        packet, client = recv.recvfrom(int(port))
        recvPacket = str(packet, "utf8")
        print("Mensagem recebida: ", recvPacket, client)
        if recvPacket == "SENDTIME":
            sleep(adelay/1000)
            sleep(ptime/1000)
            myTsStr = str(datetime.datetime.timestamp(myTime))
            print("Executando ordem de envio de tempo", datetime.datetime.fromtimestamp(datetime.datetime.timestamp(myTime)).time())
            send.sendto(myTsStr.encode(), (str(client[0]), 1024))
        else:
            #atualizo o tempo
            print("Ajustando tempo em", recvPacket, "s")
            #no envio de tempo no master usar datetime.encode
            date_str = recvPacket
            date_ts = float(recvPacket)
            real_date = datetime.datetime.timestamp(myTime) + date_ts
            myTime = datetime.datetime.fromtimestamp(real_date)
            print("Meu novo tempo: ", myTime.time())
