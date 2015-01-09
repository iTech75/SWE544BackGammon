__author__ = 'Tekin.Aytekin'
import socket
import threading
import Queue
import Player
import BGGame
import random
import Logger


class BGServer(threading.Thread):
    TIMEOUT_TO_FIND_OPPONENT = 20
    MAX_NUM_OF_USERS = 10
    MAX_NUM_OF_SPECTATORS = 10
    HEARTBEAT_INTERVAL = 30

    def __init__(self, logger):
        threading.Thread.__init__(self)
        self.__serverSocket = socket.socket()
        self.__playerDictionary = {}
        self.__clientQueue = Queue.Queue(BGServer.MAX_NUM_OF_USERS)
        self.__gameList = []

        assert isinstance(logger, Logger.Logger)
        self.__logger = logger

    def run(self):
        self.__serverSocket.bind(("", 18475))
        self.__serverSocket.listen(5)
        running = True
        self.log_message("Server started!")
        while running:
            client_socket, client_address = self.__serverSocket.accept()
            new_player = Player.Player(self, client_socket, client_address)
            self.add_player_to_dictionary(client_address, new_player)
            new_player.start()
            self.log_message("New player arrives to the server,IP:%s, Port:%s" % client_address)
            if __debug__:
                print "New player arrives to the server"

    def add_player_to_dictionary(self, client_address, new_player):
        self.__playerDictionary[client_address] = new_player
        self.log_message("Player added to the dictionary, %s" % new_player.playerName)

    def remove_player(self, client_address, player_name):
        self.__playerDictionary.pop(client_address, None)
        self.log_message("Player removed from dictionary, %s" % player_name)

    def is_user_exists(self, user_name):
        for user in self.__playerDictionary.values():
            assert isinstance(user, Player.Player)
            if user.playerName == user_name and user.isConnected:
                return True

        return False

    def __add_to_play_queue(self, player):
        self.__clientQueue.put(player)
        self.log_message("Player added to the PLAY queue, %s" % player.playerName)

    def find_opponent(self, player):
        assert isinstance(player, Player.Player)
        if self.__clientQueue.qsize() < 1:
            self.__add_to_play_queue(player)
            # Only we are at the queue waiting for an opponent
            return None
        else:
            item = self.__clientQueue.get()
            if item.playerName != player.playerName and item.isConnected:
                self.log_message("opponent found for player %s, opponent name is %s" % (player.playerName, item.playerName))
                return item
            else:
                self.__add_to_play_queue(item)

        return None

    def find_game(self):
        try:
            count = len(self.__gameList)
            if count > 0:
                order = random.randint(0, count - 1)
                game = self.__gameList[order]
                self.log_message("Game found for the spectator, player names of the game are %s and %s" %
                                 (game.blackPlayer.playerName, game.whitePlayer.playerName))
                return game
            else:
                return None
        except IndexError:
            return None

    def create_game(self, black, white):
        game = BGGame.BGGame(self, black, white)
        self.__gameList.append(game)
        game.start()
        self.log_message("Game created and started for players: (gameId:%s), players: %s and, %s" %
                         (game.gameId, game.blackPlayer.playerName, game.whitePlayer.playerName))

    def remove_game(self, game):
        self.__gameList.remove(game)
        self.log_message("Game removed from list (game_id:%s)" % game.gameId)

    def is_server_available(self):
        return self.__playerDictionary.__len__() < BGServer.MAX_NUM_OF_USERS

    def log_message(self, message):
        self.__logger.log_message(message)


# Main Module --------------------------------------------------------------------
def main():
    import BGServer
    log_queue = Queue.Queue()
    logger = Logger.Logger("BGServer.log", log_queue)
    logger.start()

    server = BGServer.BGServer(logger)
    server.start()

if __name__ == "__main__":
    main()