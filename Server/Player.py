__author__ = 'Tekin.Aytekin'
import socket
import threading
import BGServer


class Player(threading.Thread):
    def __init__(self, server, client_socket, client_address):
        threading.Thread.__init__(self)

        assert isinstance(server, BGServer.BGServer)
        assert isinstance(client_socket, socket.socket)
        assert isinstance(client_address, tuple)

        self.__server = server
        self.__clientSocket = client_socket
        self.__clientAddress = client_address

    def run(self):
        while 1:
            pass
