import sys
import socket
from time import sleep
import datetime

#leitura de variaveis de inicializacao por parametro
try:
    id = sys.argv[1]
    host = sys.argv[2]
    port = sys.argv[3]
    inputs = sys.argv[4].split(":")
    #100,1,1 dummy date for years months days
    myTime = datetime.datetime(100,1,1, int(inputs[0]), int(inputs[1]), 0) + datetime.timedelta(seconds=float(inputs[2]))
    ptime = float(sys.argv[5])
    adelay = float(sys.argv[6])
except IndexError:
    print("ERROR: invalid parameters")
    sys.exit(0)

#Variaveis de controle do tempo de que deve ser chamado calculo mestre
cooldown = 30
berkeley = 0

date_format = '%Y-%m-%d %H:%M:%S'

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
    times.append(myTime)
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
        date_obj = datetime.datetime.strptime(date_str, date_format)
        print("TIME:", date_obj, client)
        times.append(date_obj)
    tList = times.copy()
    #(aqui fica o calculo aritmetico usando tList)
    #while flag != true
    #   media de valores em times
    #   check se ninguem distoa > 10s se distoa removo da lista e chama media de novo
    #   caso todos distoem o avg vira myTime
    #   se ninguem distoa seto flag == false
    #   
    #com a media calculo tp1 = avg - times[tp1] + rtt/2
    #lista times order == nodes.txt order, logo for node in ipPortas...
    #send atualizacao do tempo (qual tempo deve ser imposto aos nodos)
    
    print("Enviando mensagem para todos nodos, ordem: UPDATETIME")
    #ajustar for para percorrer 2 listas -> tempos atualizados e de nodos
    for node in ipPortas:
        print("Enviando ordem de atualizacao de tempo para o nodo de IP:PORTA", node)
        #           myTime é o tempo que o nodo deve por
        send.sendto(myTime, (node.split(":")[0], int(node.split(":")[1])))

#processo mestre sempre sera o com id 0
if id == '0':
    print("Inicializando processo mestre...")
    print(myTime.time())
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
            myTimeStr = str(myTime)
            send.sendto(myTimeStr.encode(), (str(client[0]), 1024))
        else:
            #atualizo o o tempo
            print("Executando ordem de atualizacao de tempo para", recvPacket.split(";")[1])
            #no envio de tempo no master usar datetime.encode
            date_str = recvPacket.decode()
            date_obj = datetime.datetime.strptime(date_str, date_format)
            myTime = date_obj
            print("Meu novo tempo: ", myTime)

