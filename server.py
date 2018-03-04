import socket
import cv2
import numpy
import sys
import thread
import struct
import time
import os

'''
DATA STRUCTURES
'''
class GenericSocket():
    def __init__(self, socket):
        self.socket = socket[0]
        self.addr = socket[1][0]
        self.port = socket[1][1]

    def sendData(self, data):
        pass

    def close(self):
        pass

    def getAddr(self):
        return self.addr

    def getPort(self):
        return self.port

class UDPSocket(GenericSocket):
    def __init__(self, socket):
        self.addr = socket[0]
        self.port = socket[1]
        self.time = time.time()

    def sendData(self, data):
        if (time.time() - self.getTime() < 90):
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                sock.sendto(data,(self.addr, self.port))    
            except:
                pass
        else:
            raise Exception("Cerrar socket")

    def beat(self):
        self.time = time.time()

    def getTime(self):
        return self.time

    def close(self):
        pass

class TCPSocket(GenericSocket):
    def __init__(self, socket):
        self.socket = socket[0]
        self.addr = socket[1][0]
        self.port = socket[1][1]

    def sendData(self, data):
    	length = len(data)
    	self.socket.sendall(struct.pack('>I', length))
    	self.socket.sendall(data)

    def close(self):
        self.socket.close()


'''
ASYNCHRONIC FUNCTIONS
'''
def acceptTCP(tcpSocket, clientList):
    tcpSocket.listen(0)
    while True:
        s = TCPSocket(tcpSocket.accept())
        clientList.append(s)
        print "Se conecto el cliente " + s.getAddr() + " mediante el puerto " + str(s.getPort()) + " con TCP."

def acceptUDP(UDPsocket, clientList):
    while True:
        dataFromClient, address = UDPsocket.recvfrom(102400)
        clientadd = UDPSocket(address)
                                
        if not clientList:
            clientList.append(clientadd)
            clientadd.beat()
            print "Se conecto el cliente " + clientadd.getAddr() + " mediante el puerto " + str(clientadd.getPort()) + " con UDP."
        else:
            encontre = False
            for client in clientList:
                if (client.getAddr() == address[0] and client.getPort() == address[1]):
                    encontre = True
                    client.beat()
                    break            
            if (not encontre):
                clientList.append(clientadd)
                print "Se conecto el cliente " + clientadd.getAddr() + " mediante el puerto " + str(clientadd.getPort()) + " con UDP."

def sendFrame(capture, encode_param, clientList, isVideo):
    frame_counter = 0
    while True:
        ret, frame = capture.read()
        result, img = cv2.imencode('.jpg', frame, encode_param)
        data = numpy.array(img).tostring()
        for cli in clientList:
            try:
                cli.sendData(data)
            except:
                print "El cliente " + cli.getAddr() + " de puerto " + str(cli.getPort()) + " se ha desconectado."
                cli.close()
                clientList.remove(cli)
        
        #RESET VIDEO
        frame_counter += 1
        if isVideo and frame_counter == capture.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
            frame_counter = 0
            capture.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, 0)

'''
MAIN EXECUTION
'''
def main(file, ip_addr, tcp_port, udp_port):
    try:
        IP = ip_addr
        UDP_PORT = int(udp_port)
        TCP_PORT = int(tcp_port)

        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        tcpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        tcpSocket.bind((IP, TCP_PORT))
        udpSocket.bind((IP, UDP_PORT))

        clientList = []

        isVideo = False
        if(file == '0'):
            capture = cv2.VideoCapture(0)
        else:
            isVideo = True
            capture = cv2.VideoCapture(file)
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

        thread.start_new_thread(acceptTCP, (tcpSocket, clientList))
        thread.start_new_thread(acceptUDP, (udpSocket, clientList))
        thread.start_new_thread(sendFrame, (capture, encode_param, clientList, isVideo))

        while True:
            pass
    
    except KeyboardInterrupt:
        for cli in clientList:
            cli.sendData("BYE")            
            cli.close()
            print "Se cierra: " + cli.getAddr() + " "+ str(cli.getPort())
            #clientList.remove(cli)
        #tcpSocket.close()
        del clientList
        os._exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 5:
        main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print "Usage:\n"
        print "./server.py file(0 for camera) ip_addr tcp_port udp_port\n"

        #DEBUG
