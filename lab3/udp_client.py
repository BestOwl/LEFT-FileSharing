from socket import *
serverName = "127.0.0.1"
serverPort = 40002
clientSocket = socket(AF_INET, SOCK_DGRAM)

f = open("xjtlu.jpg", "rb")
buffer = f.read(-1)
bufferLen = len(buffer)
print(f"Sending xjtlu.jpg, file size: {bufferLen}")
clientSocket.sendto(bufferLen.to_bytes(length=4, byteorder="big", signed=False),
                    (serverName, serverPort))
clientSocket.sendto(buffer, (serverName, serverPort))
f.close()
clientSocket.close()
print("File send successfully!")