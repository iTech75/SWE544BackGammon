__author__ = 'Tekin'
import threading
import socket
import time
import BGServer
import select


class BGHeartbeat(threading.Thread):

    def __init__(self, bgserver):
        threading.Thread.__init__(self)
        assert isinstance(bgserver, BGServer.BGServer)
        self.__bgserver = bgserver

        self.__heartbeat_socket = socket.socket()
        self.clients = {}
        self.disconnectedClients = []

        self.bgheartbeatWorker = BGHeartbeatWorker(bgserver, self)
        self.__running = False

    def __del__(self):
        self.__heartbeat_socket.close()

    def run(self):
        self.bgheartbeatWorker.start()

        self.__heartbeat_socket.bind(('', 18476))
        self.__heartbeat_socket.listen(5)
        self.__running = True
        self.__bgserver.log_message("Heartbeat thread started!")
        while self.__running:
            client_socket, client_address = self.__heartbeat_socket.accept()
            self.__bgserver.log_message("New heartbeat client connected, IP:%s, Port:%s" % client_address)
            user_name = client_socket.recv(1024)
            self.clients[client_socket] = user_name
        self.__bgserver.log_message("Heartbeat is closing!")

    def stop(self):
        self.__running = False
        for s in self.clients.keys():
            try:
                s.close()
            except socket.error:
                pass
        try:
            self.__heartbeat_socket.close()
        except socket.error:
            pass


class BGHeartbeatWorker(threading.Thread):
    def __init__(self, bgserver, bgheartbeat):
        threading.Thread.__init__(self)
        assert isinstance(bgserver, BGServer.BGServer)
        assert isinstance(bgheartbeat, BGHeartbeat)

        self.__bgserver = bgserver
        self.__bgheartbeat = bgheartbeat
        self.__running = False

    def run(self):
        self.__running = True
        self.__bgserver.log_message("Heartbeat worker initiated")
        while self.__running:
            time.sleep(BGServer.BGServer.HEARTBEAT_INTERVAL)
            try:
                if self.__running:
                    self.check()
            except select.error:
                self.__bgserver.log_message("Heartbeat check error, will try in next turn")

            if self.__bgheartbeat.disconnectedClients.__len__() > 0:
                self.__bgserver.notify_game_server_on_disconnected_client()
        self.__bgserver.log_message("Heartbeat working is closing!")

    def stop(self):
        self.__running = False

    def check(self):
        self.__bgserver.log_message("Heartbeat worker started client check loop!")
        check_buffer = {}
        for s in self.__bgheartbeat.clients.keys():
            check_buffer[s] = False
        for s in check_buffer.keys():
            assert isinstance(s, socket.socket)
            try:
                s.send("PING")
                self.__bgserver.log_message("PING sent to %s" % self.__bgheartbeat.clients[s])
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
                    self.__bgserver.log_message("PONG received from %s" % self.__bgheartbeat.clients[s])

            all_clients_ok = True
            for s in check_buffer.keys():
                all_clients_ok = all_clients_ok and check_buffer[s]

            elapsed_time = time.time() - start_time

        if not all_clients_ok:
            for s in check_buffer.keys():
                if not check_buffer[s] and not self.__bgheartbeat.disconnectedClients.__contains__(s):
                    client_name = self.__bgheartbeat.clients[s]
                    self.__bgheartbeat.disconnectedClients.append(client_name)
                    self.__bgheartbeat.clients.pop(s)
                    self.__bgserver.log_message("Heartbeat for %s failed!" % client_name)
        else:
            self.__bgserver.log_message("Heartbeat OK for all clients!")