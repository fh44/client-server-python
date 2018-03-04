	#!/usr/bin/python

import sys
import socket
import cv2
import numpy
import re 
from socket import error as SocketError
import struct
import time

def recvall(sock,count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf 

def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    if ((lengthbuf != None) and (len(lengthbuf) == 4)):
    	length, = struct.unpack('>I', lengthbuf)
    	buff = recvall(sock, length)
    else:
    	return None
    return buff

def recv_one_messageUDP(sock):
    return sock.recvfrom(65007)[0]    

def client(ServerIP, TypePort, NumberPort):
	try:
		sock = None
		if (TypePort == 'TCP'):
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((ServerIP, NumberPort))
		if (TypePort == 'UDP'):
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)		
			sock.sendto("HELLO", (ServerIP, NumberPort))
			timeUDP = time.time()
		while 1:
			if (TypePort == 'TCP'):
				buff = recv_one_message(sock)
				
			if (TypePort == 'UDP'):
				#Renuevo solicitud 30 segundos
				if (time.time() - timeUDP < 30 ):
					buff = recv_one_messageUDP(sock)
				else:
					sock.sendto("HELLO", (ServerIP, NumberPort))
					print "RENUEVO SUSCRIPCION"
					timeUDP = time.time()				
				#buff = recv_one_messageUDP(sock)
			if ((buff != None) and (buff != 'BYE')):
				data = numpy.fromstring(buff, dtype='uint8')
				decimg = cv2.imdecode(data, 1)
			try:
				if ((buff != None) and (buff != "BYE")):			
					cv2.imshow('Cliente',decimg)
				else:
					break
			except cv2.error:
				if (buff == "BYE"):
					break
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
	except KeyboardInterrupt:
		sock.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        client(sys.argv[1],sys.argv[2],int(sys.argv[3]))
    else:
        print ("Usage:\n./client.py ServerIP TypePort=UDP/TCP NumberPort")