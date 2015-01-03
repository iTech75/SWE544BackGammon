__author__ = 'Tekin.Aytekin'
import socket
import threading
import Queue
import Player
import BGGame


class BGServer(threading.Thread):
    TIMEOUT_TO_FIND_OPPONENT = 10
    MAX_NUM_OF_USERS = 10
    MAX_NUM_OF_SPECTATORS = 10
    HEARTBEAT_INTERVAL = 30

    def __init__(self):
        threading.Thread.__init__(self)
        self.__serverSocket = socket.socket()
        self.__playerDictionary = {}
        self.__clientQueue = Queue.Queue(BGServer.MAX_NUM_OF_USERS)
        self.__gameDictionary = {}

    def run(self):
        self.__serverSocket.bind(("", 18475))
        self.__serverSocket.listen(5)
        running = True
        while running:
            client_socket, client_address = self.__serverSocket.accept()
            new_player = Player.Player(self, client_socket, client_address)
            self.add_player_to_dictionary(client_address, new_player)
            new_player.start()
            if __debug__:
                print "New player arrives to the server"

    def add_player_to_dictionary(self, client_address, new_player):
        self.__playerDictionary[client_address] = new_player

    def remove_player(self, client_address):
        self.__playerDictionary.pop(client_address, None)

    def is_user_exists(self, user_name):
        for user in self.__playerDictionary.values():
            assert isinstance(user, Player.Player)
            if user.playerName == user_name and user.isConnected:
                return True

        return False

    def __add_to_play_queue(self, player):
        self.__clientQueue.put(player)

    def find_opponent(self, player):
        assert isinstance(player, Player.Player)
        if self.__clientQueue.qsize() < 1:
            self.__clientQueue.put(player)
            # Only we are at the queue waiting for an opponent
            return None
        else:
            item = self.__clientQueue.get()
            if item.playerName != player.playerName and item.isConnected:
                return item
            else:
                self.__clientQueue.put(item)

        return None

    def create_game(self, black, white):
        game = BGGame.BGGame(self, black, white)
        self.__gameDictionary[game.gameId] = game
        game.start()

    def is_server_available(self):
        return self.__playerDictionary.__len__() < BGServer.MAX_NUM_OF_USERS


# Main Module --------------------------------------------------------------------
def main():
    import BGServer
    server = BGServer.BGServer()
    server.start()

if __name__ == "__main__":
    main()