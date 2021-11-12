#Python 3
#Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8
from socket import *
import sys
import pickle
import time
import random

#Server would be running on the same host as Client
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
fileName = str(sys.argv[3])
mws = int(sys.argv[4])
mss = int(sys.argv[5])
window_size = int(mws//mss)
time_out = float(sys.argv[6])
pdrop = float(sys.argv[7])
seed = float(sys.argv[8])
random.seed(seed)
set_syn = True
set_fin = False
connected = False
clientSocket = socket(AF_INET, SOCK_DGRAM)
sendBase=0
sendBase_count=0
nextSeqNum=0
ackNum=0

file = open(fileName,"r")
bytes = file.read()
file.close()

total_bytes=len(bytes)
total_segments=0
total_dropped=0
total_retran=0
total_dup=0

sender_log = open("Sender_log.txt","w")

class Timer:
    is_alive=False

    def __init__(self,start_time,time_out):
        self.start_time = start_time
        self.time_out = time_out
    
    def start(self):
        self.is_alive = True
        self.start_time = time.time()*1000
    
    def stop(self):
        self.is_alive = False
    
    def timeout(self):
        return time.time()*1000 - self.start_time >= self.time_out

def send_pck(syn,fin,ack,seq_num,ack_num,data):
    clientMessageList=[str(syn),str(fin),str(ack),str(seq_num),str(ack_num),data]
    clientMessage = ",".join(clientMessageList)
    clientSocket.sendto(clientMessage.encode('utf-8'),(serverName, serverPort))

def update_log(action,type,seq_num,num_bytes,ack_num):
    log = "{:<5} {:<10}  {:<3}  {:<5}  {:<3}  {:<5}\n".format(action,
        round((time.time()-start_time)*1000,3),type,seq_num,num_bytes,ack_num)
    sender_log.write(log)

timer = Timer(time.time()*1000,time_out)
start_time = time.time()
while(1):
    if set_syn:
        send_pck(1,0,0,nextSeqNum,ackNum,"")
        update_log("snd","S",sendBase,0,0)
        set_syn=False
        sendBase+=1
        nextSeqNum+=1
        pass
    
    # Timeout
    if connected and timer.timeout(): 
        sendBase_count=0
        data = bytes[sendBase-1:sendBase-1+mss]
        if random.random()>pdrop:
            send_pck(0,0,0,sendBase,ackNum,data)
            update_log("snd","D",sendBase,len(data),ackNum)
        else:
            update_log("drop","D",sendBase,len(data),ackNum)
            total_dropped+=1
        print(sendBase,nextSeqNum,ackNum)
        total_retran+=1
        timer.start()
        pass

    # Send when not exceed mws
    elif connected and (nextSeqNum - sendBase < mws):
        data = bytes[nextSeqNum-1:nextSeqNum-1+mss]
        if data == "":
            set_fin = True
        else:
            if not timer.is_alive:
                timer.start()

            if random.random()>pdrop:
                send_pck(0,0,0,nextSeqNum,ackNum,data)
                update_log("snd","D",nextSeqNum,len(data),ackNum)
            else:
                update_log("drop","D",nextSeqNum,len(data),ackNum)
                total_dropped+=1
            total_segments+=1
            
            nextSeqNum+=len(data)
            #print(sendBase,nextSeqNum)
        pass
    
    try:
        # Try receive an packet from the server.
        clientSocket.settimeout(0.001)
        message, serverAddress = clientSocket.recvfrom(2048)
        decodedMessage = message.decode()
        messageList = decodedMessage.split(",")
        
        # Received Syn
        if messageList[0] == "1":
            
            update_log("rcv","SA",messageList[3],0,messageList[4])
            send_pck(0,0,1,nextSeqNum,ackNum,"")
            update_log("snd","A",nextSeqNum,0,ackNum)

            connected=True
            ackNum=int(messageList[3])+1


        # Received Fin
        elif messageList[1] == "1":
            update_log("rcv","FA",messageList[3],0,messageList[4])
            send_pck(0,0,1,nextSeqNum,ackNum,"")            
            update_log("snd","A",nextSeqNum,0,ackNum)

            ackNum=int(messageList[3])+1
            break

        # Received Ack
        elif messageList[2] == "1":
            #Send next packet
            ack=int(messageList[4])
            #print(messageList,sendBase_count)
            #print(sendBase,ack)
            update_log("rcv","A",messageList[3],0,messageList[4])

            if ack>sendBase:
                sendBase = ack
                if sendBase != nextSeqNum:
                    timer.start()
            elif ack == sendBase:
                total_dup+=1
                sendBase_count+=1

                # Fast retransmission
                if sendBase_count == 3:
                    print("send_count is 3",sendBase)
                    sendBase_count = 0
                    data = bytes[sendBase-1:sendBase-1+mss]
                    print(sendBase,nextSeqNum,ackNum)
                    total_retran+=1
                    if random.random()>pdrop:
                        send_pck(0,0,0,sendBase,ackNum,data)
                        update_log("snd","D",sendBase,len(data),ackNum)
                    else:
                        update_log("drop","D",sendBase,len(data),ackNum)
                        total_dropped+=1
                    timer.start()

    except Exception as e:
        #print(e)
        pass
    
    if set_fin and sendBase == nextSeqNum:
        send_pck(0,1,0,nextSeqNum,ackNum,"")
        update_log("snd","F",nextSeqNum,0,ackNum)
        nextSeqNum+=1
        set_fin=False

#prepare to exit. Send Unsubscribe message to server
#message='Unsubscribe'
#clientSocket.sendto(message.encode(),(serverName, serverPort))
sender_log.write("Total bytes: " + str(total_bytes) + "\n")
sender_log.write("Total segments: " + str(total_segments) + "\n")
sender_log.write("Total dropped: " + str(total_dropped) + "\n")
sender_log.write("Total retransmitted: " + str(total_retran) + "\n")
sender_log.write("Total duplicated acks " + str(total_dup) + "\n")
sender_log.close()
clientSocket.close()
# Close the socket
