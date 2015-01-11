__author__ = 'Tekin'
import socket
import threading


class ClientHeartbeat(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.__socket = socket.socket()
        self.__userName = "None"

    def run(self):
        self.__socket.connect(("localhost", 18476))
        self.__socket.send(self.__userName)
        running = True
        while running:
            request = self.__socket.recv(1024)
            if request == "PING":
                self.__socket.send("PONG")
            else:
                self.__socket.send("ERRORINCOMMAND")

    def set_username(self, user_name):
        self.__userName = user_name