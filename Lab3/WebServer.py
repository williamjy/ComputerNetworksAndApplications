import sys
from socket import *
from datetime import datetime

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)
print("The server is ready to receive")
while 1:
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024)
    rows = sentence.split()    
    try:
        data = open(rows[1][1:], 'rb').read()
        connectionSocket.send('HTTP/1.1 200 OK\r\n'.encode())
        print('HTTP/1.1 200 OK')
        if 'png' in str(rows[1][1:]):
            connectionSocket.send('Content-Type: image/png \r\n\r\n'.encode())
            print('Content-Type: image/png')
        if 'html' in str(rows[1][1:]):
            connectionSocket.send('Content-Type: text/html \r\n\r\n'.encode())
            print('Content-Type: text/html')
        connectionSocket.send(data)
        print(rows[1][1:])
    except IOError:
        connectionSocket.send('HTTP/1.1 404 File NOT FOUND\r\n'.encode())
        print('HTTP/1.1 404 File NOT FOUND')
        connectionSocket.send('Content-Type: text/html \r\n\r\n'.encode())
        connectionSocket.send('<html><h1>404 File Not Found</h1><p>Try index.html or myimage.png !</p></html>'.encode())
connectionSocket.close()
