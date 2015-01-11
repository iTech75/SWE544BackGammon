__author__ = 'Tekin'
import socket
import threading


class ClientHeartbeat(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.__socket = socket.socket()
        self.__userName = "None"
        self.__running = False

    def __del__(self):
        self.__socket.close()

    def run(self):
        self.__socket.connect(("localhost", 18476))
        self.__socket.send(self.__userName)
        self.__running = True
        while self.__running:
            try:
                request = self.__socket.recv(1024)
                if request == "PING":
                    self.__socket.send("PONG")
                else:
                    self.__socket.send("ERRORINCOMMAND")
            except socket.error:
                self.__running = False
        self.__socket.close()

    def set_username(self, user_name):
        self.__userName = user_name

    def stop(self):
        self.__running = False
        self.__socket.close()