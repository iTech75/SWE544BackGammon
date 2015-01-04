__author__ = 'Tekin.Aytekin'
import socket
import threading
import time
import BGServer
import BGGame


class Player(threading.Thread):
    def __init__(self, bgserver, client_socket, client_address):
        threading.Thread.__init__(self)

        assert isinstance(bgserver, BGServer.BGServer)
        assert isinstance(client_socket, socket.socket)
        assert isinstance(client_address, tuple)

        self.__bgserver = bgserver
        self.__clientSocket = client_socket
        self.__clientAddress = client_address
        self.isConnected = False
        self.playerName = "name"
        self.__activeGame = None

    def __str__(self):
        return "%s, Ced:%s" % (self.playerName, str(self.isConnected))

    def run(self):
        """
        ***********************************************************************
        Main loop of the player...
        ***********************************************************************
        """
        running = True
        while running:
            try:
                request = self.__clientSocket.recv(1024)
                response = self.__parse_request(request)
                self.__clientSocket.send(response)
                # if game has been commenced then wait for it to conclude
                while self.__activeGame is not None:
                    time.sleep(3)
            except socket.error as e:
                print "Exception occurred, message is : " + e.strerror + "_" + str(e.errno)
                running = False

        self.__clientSocket.close()
        self.__bgserver.remove_player(self.__clientAddress)
        print self.playerName + " is disconnected..."

    def __parse_request(self, request):
        """
        user request parsed here, protocol lives here
        """
        if request == "" or request is None:
            return "ERRORINCOMMAND"
        commands = request.split("|")

        if commands[0] == "CONNECT":
            return self.__connect(commands)
        elif commands[0] == "PLAY" and self.__activeGame is None:
            return self.__play(commands)
        elif commands[0] == "WATCH" and self.__activeGame is None:
            return self.__watch(commands)
        else:
            return "ERRORINCOMMAND"

    def __connect(self, commands):
        assert isinstance(commands, list)
        if len(commands) == 2:
            self.playerName = commands[1]
            if self.__bgserver.is_user_exists(self.playerName):
                return "USEREXISTS"
            if not self.__bgserver.is_server_available():
                return "BUSY"
            else:
                self.isConnected = True
                return "OK"
        return "ERRORINCOMMAND"

    def __play(self, commands):
        assert isinstance(commands, list)
        opponent = self.__bgserver.find_opponent(self)

        if opponent is not None:
            import Player
            assert isinstance(opponent, Player.Player)
            self.__bgserver.create_game(self, opponent)
            color = "w"
            if self.__activeGame.blackPlayer == self:
                color = "b"
            return "OPPONENT|%s|%s" % (opponent.playerName, color)
        else:
            # game queue is empty, wait for someone else to select you!
            while self.__activeGame is None:
                time.sleep(3)
            if self.__activeGame is not None:
                if self.__activeGame.whitePlayer != self:
                    return "OPPONENT|%s|%s" % (self.__activeGame.whitePlayer.playerName, "b")
                else:
                    return "OPPONENT|%s|%s" % (self.__activeGame.blackPlayer.playerName, "w")

    def __watch(self, commands):
        assert isinstance(commands, list)
        game = self.__bgserver.find_game()

        if game is not None:
            import BGGame
            assert isinstance(game, BGGame.BGGame)
            if len(game.spectators) < BGServer.BGServer.MAX_NUM_OF_SPECTATORS:
                game.add_spectator(self)
                # let's use this for watch also it's likely we will create another identifier for watch mode
                self.__activeGame == game
                return "ID|%s|%s|%s" % (game.gameId, game.blackPlayer.playerName, game.whitePlayer.playerName)
            else:
                return "BUSY"
        else:
            # No active gane
            return "NOACTIVEMATCHUP"

    def set_game(self, game):
        assert isinstance(game, BGGame.BGGame)
        if self.__activeGame is None:
            self.__activeGame = game
        else:
            if game is None:
                self.__activeGame = None
            else:
                raise Exception("There is already an active game this player is involved!")

    def send_message(self, message):
        self.__clientSocket.send(message)
        response = self.__clientSocket.recv(1024)
        return response