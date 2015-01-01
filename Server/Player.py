__author__ = 'Tekin.Aytekin'
import socket
import threading
import BGServer


class Player(threading.Thread):
    def __init__(self, bgserver, client_socket, client_address):
        threading.Thread.__init__(self)

        # assert isinstance(bgserver, BGServer.BGServer)
        assert isinstance(client_socket, socket.socket)
        assert isinstance(client_address, tuple)

        self.__bgserver = bgserver
        self.__clientSocket = client_socket
        self.__clientAddress = client_address
        self.__isConnected = False
        self.__playerName = "name"

    def run(self):
        """
        Main loop of the server...
        """
        while 1:
            request = self.__clientSocket.recv(1024)
            response = self.__parse_request(request)
            self.__clientSocket.send(response)

    def __parse_request(self, request):
        """
        user request parsed here, protocol lives here
        """
        if request == "" or request is None:
            return "ERRORINCOMMAND"
        commands = request.split("|")

        if commands[0] == "CONNECT":
            return self.__connect(commands)
        else:
            return "ERRORINCOMMAND"

    def __connect(self, commands):
        assert isinstance(commands, list)

        if len(commands) != 2:
            return "ERRORINCOMMAND"

        self.__playerName = commands[1]
        self.__isConnected = True

        return "OK"