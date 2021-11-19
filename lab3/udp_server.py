from socket import *

serverPort = 40002
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", serverPort))
print(f"Simple UDP file server started on port {serverPort}")

while True:
    bufferLen = serverSocket.recv(4)
    bufferLen = int().from_bytes(bufferLen, byteorder="big", signed=False)
    outBuffer = serverSocket.recv(bufferLen)
    f = open("xjtlu1.jpg", "wb")
    f.write(outBuffer)
    f.close()
    print("Received file has been saved to xjtlu1.jpg")
