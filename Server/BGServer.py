import Player

__author__ = 'Tekin.Aytekin'
import socket
import threading


class BGServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.__serverSocket = socket.socket()
        self.__playerDictionary = {}

    def run(self):
        self.__serverSocket.bind(("localhost", 18475))
        self.__serverSocket.listen(5)
        while 1:
            client_socket, client_address = self.__serverSocket.accept()
            new_player = Player.Player(self, client_socket, client_address)
            self.add_player_to_dictionary(client_address, new_player)
            new_player.start()
            if __debug__:
                print "New player arrives to the server"

    def add_player_to_dictionary(self, client_address, new_player):
        self.__playerDictionary[client_address] = new_player
        new_player.start()


# Main Module --------------------------------------------------------------------
def main():
    server = BGServer()
    server.start()

if __name__ == "__main__":
    main()