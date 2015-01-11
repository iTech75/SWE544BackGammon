__author__ = 'Tekin.Aytekin'
import socket
import threading
import Queue
import Player
import BGGame
import random
import Logger
import BGHeartbeat


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
        self.__heartbeat = BGHeartbeat.BGHeartbeat(self)

    def __del__(self):
        self.__heartbeat.stop()
        self.__serverSocket.close()
        self.__logger.stop()

    def run(self):
        self.__heartbeat.start()
        self.__serverSocket.bind(("", 18475))
        self.__serverSocket.listen(5)
        running = True
        self.log_message("Server started!")
        while running:
            client_socket, client_address = self.__serverSocket.accept()
            self.log_message("New player arrives to the server,IP:%s, Port:%s" % client_address)
            new_player = Player.Player(self, client_socket, client_address)
            self.add_player_to_dictionary(client_address, new_player)
            new_player.start()
            self.log_message("New player started: IP:%s, Port:%s" % client_address)
            if __debug__:
                print "New player arrives to the server"
        self.__serverSocket.close()
        self.log_message("Server is closed!")

    def add_player_to_dictionary(self, client_address, new_player):
        self.__playerDictionary[client_address] = new_player
        self.log_message("Player added to the dictionary, Ip:%s, Port:%s" % new_player.clientAddress)

    def remove_player(self, client_address):
        player = self.__playerDictionary.pop(client_address, None)
        if player:
            assert isinstance(player, Player.Player)
            player.isConnected = False
            self.log_message("Player removed from dictionary, %s" % player.playerName)

    def is_user_exists(self, user_name):
        for user in self.__playerDictionary.values():
            assert isinstance(user, Player.Player)
            if user.playerName == user_name and user.isConnected:
                self.log_message("User exists, client must choose another name %s" % user_name)
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
                self.log_message("Opponent found for player %s, opponent name is %s" %
                                 (player.playerName, item.playerName))
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
        self.log_message("Game created and started for players: (gameId:%s), players: %s vs. %s" %
                         (game.gameId, game.blackPlayer.playerName, game.whitePlayer.playerName))

    def remove_game(self, game):
        self.__gameList.remove(game)
        self.log_message("Game removed from list (game_id:%s)" % game.gameId)

    def is_server_available(self):
        result = self.__playerDictionary.__len__() < BGServer.MAX_NUM_OF_USERS
        if not result:
            self.log_message("Server is FULL")
        return result

    def log_message(self, message):
        self.__logger.log_message(message)

    def notify_game_server_on_disconnected_client(self):
        for name in self.__heartbeat.disconnectedClients:
            for player in self.__playerDictionary.values():
                if player.playerName == name:
                    self.log_message("Disconnected client found: %s" % name)
                    self.remove_player(player.clientAddress)
                    game = player.get_game()
                    if game is not None:
                        self.log_message("Trying to end of the game of the disconnected client, %s" % name)
                        assert isinstance(game, BGGame.BGGame)
                        game.player_left(player)


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