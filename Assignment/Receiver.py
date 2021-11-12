# Sample code for Multi-Threaded Server
#Python 3
# Usage: python3 UDPserver3.py
#coding: utf-8
from socket import *
import sys
import threading
import time
import datetime as dt
import pickle

#Server will run on this port
serverPort = int(sys.argv[1])
fileName = str(sys.argv[2])
t_lock=threading.Condition()
#will store clients info in this list
clients=[]
# would communicate with clients after every second
UPDATE_INTERVAL= 1
timeout=False
nextSeqNum=0
ackNum=0
expected_seq=0
pck_buffer=dict()
file=open(fileName,"w")

def recv_handler():
    global nextSeqNum
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    #print('Server is ready for service')
    while(1):
        try:
            message, clientAddress = serverSocket.recvfrom(2048)
            decodedMessage = message.decode()
            messageList = decodedMessage.split(",")
            with t_lock:
                if messageList[0] == "1" :
                    clients.append(clientAddress)
                    ackNum=int(messageList[3])+1
                    serverMessageList = ["1","0","1",str(nextSeqNum),str(ackNum),""]
                    serverMessage=",".join(serverMessageList)
                    serverSocket.sendto(serverMessage.encode(), clientAddress)
                    #print("Sent: "+serverMessage)
                    nextSeqNum+=1

                elif messageList[1] == "1":
                    ackNum=int(messageList[3])+1
                    serverMessageList = ["0","1","1",str(nextSeqNum),str(ackNum),""]
                    serverMessage=",".join(serverMessageList)
                    serverSocket.sendto(serverMessage.encode(), clientAddress)
                    #print("Sent: "+serverMessage)
                    break
                elif messageList[2] == "1":
                    #recieved ack
                    pass

                else:
                    received_seq = int(messageList[3])
                    data=messageList[5]
                    
                    print(list(pck_buffer.keys()))
                    if received_seq == ackNum:
                        ackNum=received_seq+len(messageList[5])
                        file.write(data)

                        while ackNum in pck_buffer.keys():
                            data=pck_buffer[ackNum]
                            file.write(data)
                            pck_buffer.pop(ackNum)
                            ackNum+=len(data)

                    elif received_seq > ackNum:
                        pck_buffer[received_seq]=data
                        #print("Larger: ",ackNum,received_seq)

                    #print("received: "+str(received_seq))
                    serverMessageList = ["0","0","1",str(nextSeqNum),str(ackNum),""]
                    serverMessage=",".join(serverMessageList)
                    serverSocket.sendto(serverMessage.encode(), clientAddress)
                    #print("Sent: "+serverMessage)
                t_lock.notify()
        except Exception as e:
            #print(e)
            pass
    serverSocket.close()
    file.close()
print(pck_buffer)

"""def send_handler():
    global t_lock
    global clients
    global clientSocket
    global serverSocket
    global timeout
    #go through the list of the subscribed clients and send them the current time after every 1 second
    while(1):
        #get lock
        with t_lock:
            for i in clients:
                currtime =dt.datetime.now()
                date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")
                message='Current time is ' + date_time
                clientSocket.sendto(message.encode(), i)
            #print('Sending time to', i[0], 'listening at', i[1], 'at time ', date_time)
            #notify other thread
            t_lock.notify()
        #sleep for UPDATE_INTERVAL
        time.sleep(UPDATE_INTERVAL)"""

#we will use two sockets, one for sending and one for receiving
clientSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind(('localhost', serverPort))
recv_handler()

"""
recv_thread=threading.Thread(name="RecvHandler", target=recv_handler)
recv_thread.daemon=True
recv_thread.start()

send_thread=threading.Thread(name="SendHandler",target=send_handler)
send_thread.daemon=True
send_thread.start()
#this is the main thread
while True:
    time.sleep(2)"""

