__author__ = 'Tekin'
import threading
import BGServer
import random
import Player


class GamePoint:
    def __init__(self, point_id, color, count):
        self.pointId = point_id
        self.color = color
        self.count = count


class BGGame(threading.Thread):
    gameIdCounter = 0
    counterLock = threading.Lock()

    def __init__(self, bgserver, black, white):
        threading.Thread.__init__(self)

        assert isinstance(bgserver, BGServer.BGServer)
        assert isinstance(black, Player.Player)
        assert isinstance(white, Player.Player)

        self.__bgserver = bgserver
        self.blackPlayer = black
        self.whitePlayer = white
        self.gameId = BGGame.get_new_id()
        self.blackPlayer.set_game(self)
        self.whitePlayer.set_game(self)

        self.__gameStatus = [GamePoint(0, "", 0) for x in range(27)]
        self.__previous_gamestate = [""] * 26

    def __initilize(self):
        i = 0
        for item in self.__gameStatus:
            item.pointId = i
            item.color = ""
            item.count = 0

        self.__gameStatus[1].color = "w"
        self.__gameStatus[1].count = 2

        self.__gameStatus[6].color = "b"
        self.__gameStatus[6].count = 5

        self.__gameStatus[8].color = "b"
        self.__gameStatus[8].count = 3

        self.__gameStatus[12].color = "w"
        self.__gameStatus[12].count = 5

        self.__gameStatus[13].color = "b"
        self.__gameStatus[13].count = 5

        self.__gameStatus[17].color = "w"
        self.__gameStatus[17].count = 3

        self.__gameStatus[19].color = "w"
        self.__gameStatus[19].count = 5

        self.__gameStatus[24].color = "b"
        self.__gameStatus[24].count = 2

    def __create_game_status_string(self):
        result = ""
        for i in range(1, 25):
            if self.__gameStatus[i].color != "":
                result += "|%d%s%d" % (i, self.__gameStatus[i].color, self.__gameStatus[i].count)
        return result

    def run(self):
        self.__initilize()
        running = True
        roll = self.blackPlayer
        while running:
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)

            message = "YOURTURN|%d-%d" % (dice1, dice2)
            response = roll.send_message(message)
            self.__parse_response(response, roll)

            message = "SETSTATUS" + self.__create_game_status_string()
            response = self.blackPlayer.send_message(message)
            if response != "OK":
                raise Exception("Unexpected response: " + response)

            response = self.whitePlayer.send_message(message)
            if response != "OK":
                raise Exception("Unexpected response: " + response)

            if roll == self.blackPlayer:
                roll = self.whitePlayer
            else:
                roll = self.blackPlayer

    def __parse_response(self, response, roll):
        data = response.split("|")
        if data[0] == "MOVE":
            self.__parse_backgammon_notation(data[1], roll)

    def __parse_backgammon_notation(self, move, roll):
        data = move.split(",")
        for item in data:
            source_target = item.split("/")
            if len(source_target) == 2:
                if roll == self.whitePlayer:
                    source_target[0] = 25 - int(source_target[0])
                    source_target[1] = 25 - int(source_target[1])

                self.__gameStatus[int(source_target[0])].count -= 1
                if self.__gameStatus[int(source_target[0])].count <= 0:
                    self.__gameStatus[int(source_target[0])].count = 0
                    self.__gameStatus[int(source_target[0])].color = ""

                self.__gameStatus[int(source_target[1])].count += 1
                if self.__gameStatus[int(source_target[1])].count > 0:
                    if roll == self.blackPlayer:
                        self.__gameStatus[int(source_target[1])].color = "b"
                    else:
                        self.__gameStatus[int(source_target[1])].color = "w"

    @staticmethod
    def get_new_id():
        BGGame.counterLock.acquire()
        try:
            BGGame.gameIdCounter += 1
            return "G%05d" % BGGame.gameIdCounter
        finally:
            BGGame.counterLock.release()
        pass