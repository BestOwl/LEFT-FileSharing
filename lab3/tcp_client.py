from socket import *
serverName = "127.0.0.1"
serverPort = 40001
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

f = open("xjtlu.jpg", "rb")
buffer = f.read(-1)
bufferLen = len(buffer)
print(f"Sending xjtlu.jpg, file size: {bufferLen}")
clientSocket.send(bufferLen.to_bytes(length=4, byteorder="big", signed=False))
clientSocket.send(buffer)
f.close()
clientSocket.close()
print("File send successfully!")