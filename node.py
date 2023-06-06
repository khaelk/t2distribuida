import sys
import socket
from time import sleep
import datetime
import time

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

start_time = time.time()
end_time = 0

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
    global start_time
    global end_time
    print("Enviando mensagem para todos nodos, ordem: SENDTIME")
    times = []
    tList = []
    rtts = []
    for node in ipPortas:
        print("Enviando ordem de envio de tempo SENDTIME para o nodo de IP:PORTA", node)
        send.sendto(bytes("SENDTIME", "utf8"), (node.split(":")[0], int(node.split(":")[1]))) # ajustar para enviar para todos nodos
        t1 = time.time()
        try:
            recvPacket, client = recv.recvfrom(1024)
        except Exception as e:
            print("Erro no recebimento do tempo de um nodo!")
            exit()
        t4 = time.time()
        rtt = t4 - t1
        #transforma msg em bytes recebida em datetime obj
        date_str = recvPacket.decode()
        date_ts = float(date_str)
        print("Time recebido:", datetime.datetime.fromtimestamp(date_ts).time(), client)
        times.append(date_ts)
        tList.append(date_ts)
        rtts.append(rtt)
    end_time = time.time()
    tList.append(datetime.datetime.timestamp(myTime) + end_time - start_time)
    print(datetime.datetime.fromtimestamp(datetime.datetime.timestamp(myTime) + end_time - start_time))
    print(datetime.datetime.fromtimestamp(times[0]))
    avg = 0
    n = 1
    flag = False
    #(aqui fica o calculo aritmetico usando tList)
    while flag != True:
        print("Iniciando calculo de media.")
    #   caso todos distoem o avg vira myTime (master time)
        if len(tList) == 0:
            print("Tempos muito distoantes setto o meu tempo.")
            end_time = time.time()
            avg = datetime.datetime.timestamp(myTime) + end_time - start_time
            break
    #   media de valores em timestamp
        avg = (sum(tList)) / len(tList)
    #   se ninguem distoa seto flag == True finalizando calc media
        flag = True
        print("AVG", n, ":", avg)
    #   check se ninguem distoa > 10s se distoa removo da lista e chama media de novo
        tAux = []
        tAux[:] = [x for x in tList if abs(x-avg)<=mean_diff]
        print(tList, tAux)
        if len(tAux) != len(tList):
            tList = tAux
            flag = False

    print("Media final calculada:", avg)
    end_time = time.time()
    newTime = datetime.datetime.timestamp(myTime) + end_time - start_time + (avg - float(datetime.datetime.timestamp(myTime) + end_time - start_time))
    print(avg, datetime.datetime.timestamp(myTime), datetime.datetime.timestamp(myTime) + end_time - start_time)
    print("Devo adiantar meu tempo em:", (avg - float(datetime.datetime.timestamp(myTime) + end_time - start_time)), "s")
    myTime = datetime.datetime.fromtimestamp(newTime)
    print("Atualizei meu tempo para:", myTime.time())
    print("Enviando mensagem para todos nodos, ordem: UPDATETIME")
    start_time = time.time()
    #ajustar for para percorrer 2 listas -> tempos atualizados e de nodos
    index = 0
    for node in ipPortas:
        #com a media calculo tp1 = avg - times[tp1] + rtt/2
        newT = avg - times[index] + rtts[index]/2 # + RTT
        print("Enviando ordem de atualizacao de tempo para o nodo de IP:PORTA", node, newT)
        newT = str(newT)
        send.sendto(newT.encode(), (node.split(":")[0], int(node.split(":")[1])))
        index = index + 1

#processo mestre sempre sera o com id 0
if id == '0':
    print("Inicializando processo mestre...", myTime.time())
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
            end_time = time.time()
            myTsStr = str(datetime.datetime.timestamp(myTime) + end_time - start_time)
            print("Executando ordem de envio de tempo", datetime.datetime.fromtimestamp(datetime.datetime.timestamp(myTime) + end_time - start_time).time())
            send.sendto(myTsStr.encode(), (str(client[0]), 1024))
        else:
            #atualizo o tempo
            print("Ajustando tempo em", recvPacket, "s")
            #no envio de tempo no master usar datetime.encode
            date_str = recvPacket
            date_ts = float(recvPacket)
            end_time = time.time()
            real_date = datetime.datetime.timestamp(myTime) + date_ts + end_time - start_time
            myTime = datetime.datetime.fromtimestamp(real_date)
            start_time = time.time()
            print("Meu novo tempo: ", myTime.time())

