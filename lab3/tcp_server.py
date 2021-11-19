from socket import *

serverPort = 40001
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(2)
print(f"Simple file server started on port {serverPort}")

while True:
    connectionSocket, addr = serverSocket.accept()
    bufferLen = connectionSocket.recv(4)
    bufferLen = int().from_bytes(bufferLen, byteorder="big", signed=False)
    outBuffer = connectionSocket.recv(bufferLen)
    f = open("xjtlu1.jpg", "wb")
    f.write(outBuffer)
    f.close()
    print("Received file has been saved to xjtlu1.jpg")
