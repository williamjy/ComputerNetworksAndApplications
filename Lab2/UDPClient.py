#coding: utf-8
import sys
from socket import *
from datetime import datetime

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_DGRAM)
rtts = list()
for seqnum in range(3331, 3345):
    startTime = datetime.now()
    message = "PING {} {}\r\n".format(seqnum,startTime)
    clientSocket.sendto(message.encode('utf-8'),(serverName, serverPort))
    try:
        clientSocket.settimeout(0.6)
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        endTime = datetime.now()
        time = (endTime - startTime).total_seconds() * 1000
        rtts.append(time)
        print("ping to {}, seq = {}, rtt = {} ms".format(serverName, str(seqnum), time))
    except:
        print("ping to {}, seq = {}, timeout".format(serverName, str(seqnum)))
if rtts == []:
    print("Failed to connect")
else:
    print("Minimum rtt is {} ms".format(int(min(rtts))))
    print("Maximum rtt is {} ms".format(int(max(rtts))))
    print("Average rtt is {} ms".format(int(sum(rtts)/len(rtts))))
clientSocket.close()
