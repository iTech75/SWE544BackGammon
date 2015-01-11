__author__ = 'Tekin'
import threading
import socket
import time
import BGServer
import select


class BGHeartbeat(threading.Thread):

    def __init__(self, bgserver):
        threading.Thread.__init__(self)
        self.__bgserver = bgserver

        self.__heartbeat_socket = socket.socket()
        self.clients = {}
        self.disconnectedClients = []

        self.bgheartbeatWorker = BGHeartbeatWorker(bgserver, self)

    def run(self):
        self.bgheartbeatWorker.start()

        self.__heartbeat_socket.bind(('', 18476))
        self.__heartbeat_socket.listen(5)
        running = True
        while running:
            client_socket, client_address = self.__heartbeat_socket.accept()
            user_name = client_socket.recv(1024)
            self.clients[client_socket] = user_name


class BGHeartbeatWorker(threading.Thread):
    def __init__(self, bgserver, bgheartbeat):
        threading.Thread.__init__(self)
        assert isinstance(bgserver, BGServer.BGServer)
        assert isinstance(bgheartbeat, BGHeartbeat)

        self.__bgserver = bgserver
        self.__bgheartbeat = bgheartbeat

    def run(self):
        running = True
        while running:
            time.sleep(BGServer.BGServer.HEARTBEAT_INTERVAL)
            self.check()
            if self.__bgheartbeat.disconnectedClients.__len__() > 0:
                self.__bgserver.notify_game_server_on_disconnected_client()

    def check(self):
        check_buffer = {}
        for s in self.__bgheartbeat.clients.keys():
            check_buffer[s] = False
        for s in check_buffer.keys():
            assert isinstance(s, socket.socket)
            try:
                s.send("PING")
            except socket.error as e:
                self.__bgheartbeat.disconnectedClients.append(self.__bgheartbeat.clients[s])
                self.__bgheartbeat.clients.pop(s)
                check_buffer.pop(s)

        start_time = time.time()
        elapsed_time = time.time() - start_time
        all_clients_ok = False
        while elapsed_time < BGServer.BGServer.HEARTBEAT_INTERVAL and not all_clients_ok:
            rlist, wlist, xlist = select.select(self.__bgheartbeat.clients.keys(), [], [], 5)
            for s in rlist:
                response = s.recv(1024)
                if response == "PONG":
                    check_buffer[s] = True

            all_clients_ok = True
            for s in check_buffer.keys():
                all_clients_ok = all_clients_ok and check_buffer[s]

            elapsed_time = time.time() - start_time

        if not all_clients_ok:
            for s in check_buffer.keys():
                if not check_buffer[s] and not self.__bgheartbeat.disconnectedClients.__contains__(s):
                    self.__bgheartbeat.disconnectedClients.append(self.__bgheartbeat.clients[s])
                    self.__bgheartbeat.clients.pop(s)
