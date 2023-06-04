import sys
import socket
from time import sleep
import datetime

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

date_format = '%Y-%m-%d %H:%M:%S.%f'

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

#calculo feito do algoritmo
def calculo(ipPortas):
    global myTime
    print("Enviando mensagem para todos nodos, ordem: SENDTIME")
    times = []
    tList = []
    tList.append(datetime.datetime.timestamp(myTime))
    for node in ipPortas:
        print("Enviando ordem de envio de tempo SENDTIME para o nodo de IP:PORTA", node)
        send.sendto(bytes("SENDTIME", "utf8"), (node.split(":")[0], int(node.split(":")[1]))) # ajustar para enviar para todos nodos
        try:
            recvPacket, client = recv.recvfrom(1024)
        except Exception as e:
            print("Erro no recebimento do tempo de um nodo!")
            exit()
        #transforma msg em bytes recebida em datetime obj
        date_str = recvPacket.decode()
        date_ts = float(date_str)
        print("TIME:", date_ts, client)
        times.append(date_ts)
        tList.append(date_ts)

    avg = 0
    flag = False
    #(aqui fica o calculo aritmetico usando tList)
    while flag != True:
    #   caso todos distoem o avg vira myTime (master time)
        if len(tList) == 0:
            print("Tempos muito distoantes setto o meu tempo.")
            avg = datetime.datetime.timestamp(myTime)
            break
    #   media de valores em timestamp
        avg = (sum(tList)) / len(tList)
    #   se ninguem distoa seto flag == True finalizando calc media
        flag = True
        print("AVG", avg)
    #   check se ninguem distoa > 10s se distoa removo da lista e chama media de novo
        tAux = []
        tAux[:] = [x for x in tList if abs(x-avg)<=mean_diff * 1000]
        print(tList, tAux)
        if len(tAux) != len(tList):
            tList = tAux
            flag = False

    print("Media calculada:", avg)
    #lista times order == nodes.txt order, logo for node in ipPortas...
    #send atualizacao do tempo (qual tempo deve ser imposto aos nodos)
    newTime = datetime.datetime.timestamp(myTime) + (avg - datetime.datetime.timestamp(myTime))
    myTime = datetime.datetime.fromtimestamp(newTime)
    print(myTime)
    print("Atualizei meu tempo:", myTime.time())
    print("Enviando mensagem para todos nodos, ordem: UPDATETIME")
    #ajustar for para percorrer 2 listas -> tempos atualizados e de nodos
    index = 0
    for node in ipPortas:
        print("Enviando ordem de atualizacao de tempo para o nodo de IP:PORTA", node)
        #com a media calculo tp1 = avg - times[tp1] + rtt/2
        newT = avg - times[index] # + RTT
        newT = str(newT)
        send.sendto(newT.encode(), (node.split(":")[0], int(node.split(":")[1])))
        index = index + 1

#processo mestre sempre sera o com id 0
if id == '0':
    print("Inicializando processo mestre...")
    print(myTime.time())
    print(datetime.datetime.timestamp(myTime))
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
        if recvPacket == "SENDTIME":
            #envio o meu tempo
            print("Executando ordem de envio de tempo")
            #count time here
            myTsStr = str(datetime.datetime.timestamp(myTime))
            send.sendto(myTsStr.encode(), (str(client[0]), 1024))
        else:
            #atualizo o tempo
            print("Executando ordem de atualizacao de tempo para", recvPacket)
            #no envio de tempo no master usar datetime.encode
            date_str = recvPacket
            date_ts = float(recvPacket)
            real_date = datetime.datetime.timestamp(myTime) + date_ts
            myTime = datetime.datetime.fromtimestamp(real_date)
            print(myTime)
            print("Meu novo tempo: ", myTime.time())

