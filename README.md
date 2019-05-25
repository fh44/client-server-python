# client-server-python
Very simple Python client-server video streaming application

To run the application, server.py and client.py need to be called following the next order of input parameters:

client.py:
$./client.py \ ServerIP \ TypePort=UDP/TCP \ NumberPort$

server.py:
$./server.py \ file(0 \ for \ camera) \ ip\_addr \ tcp\_port \ udp\_port$

Where UDP and TCP are the two protocols accepted, and server is able to stream a file vide or through webcam.
