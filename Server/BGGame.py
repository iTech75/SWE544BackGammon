__author__ = 'Tekin'
import threading
import BGServer
import random
import Player
import string


class GamePoint:
    def __init__(self, point_id, color, count):
        self.pointId = point_id
        self.color = color
        self.count = count

    def __str__(self):
        if self.pointId == 0:
            return "bar: %s" % self.color
        elif self.pointId == 25:
            return "off: %s" % self.color
        else:
            return "%d. %s(%d)" % (self.pointId, self.color, self.count)


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

        self.gameStatus = [GamePoint(0, "", 0) for x in range(26)]
        self.__previous_gamestate = ""
        self.spectators = []

    def initialize(self):
        self.set_game_status("0/0|1w2|6b5|8b3|12w5|13b5|17w3|19w5|24b2|0/0")

    def set_game_status(self, new_status):
        i = 0
        for item in self.gameStatus:
            item.pointId = i
            item.color = ""
            item.count = 0
            i += 1

        points = new_status.split('|')

        black_bar, white_bar = points[0].split('/')
        self.gameStatus[0].color = "%s/%s" % (black_bar, white_bar)
        points.remove(points[0])

        black_off, white_off = points[len(points) - 1].split('/')
        self.gameStatus[25].color = "%s/%s" % (black_off, white_off)
        points.remove(points[len(points) - 1])

        for point in points:
            color = 'w'
            if point.find('b') > -1:
                color = 'b'
            point_id, count = point.split(color)
            point_id = int(point_id)
            self.gameStatus[point_id].color = color
            self.gameStatus[point_id].count = int(count)

    def create_game_status_string(self):
        result = ""
        for i in range(1, 25):
            if self.gameStatus[i].color != "":
                result += "|%d%s%d" % (i, self.gameStatus[i].color, self.gameStatus[i].count)
        return "|%s%s|%s" % (self.gameStatus[0].color, result, self.gameStatus[25].color)

    def run(self):
        self.initialize()
        running = True
        roll = self.blackPlayer
        redice = True
        dice1 = 1
        dice2 = 1
        while running:
            state_backup = self.create_game_status_string()[1:]
            roll_backup = roll
            previous_state_backup = self.__previous_gamestate

            if redice:
                dice1 = random.randint(1, 6)
                dice2 = random.randint(1, 6)

            redice = True  # keep rethrowing until an error
            try:
                message = "YOURTURN|%d-%d" % (dice1, dice2)
                response = roll.send_message(message)
                self.__parse_response(response, roll)

                message = "SETSTATUS" + self.create_game_status_string()
                response = self.blackPlayer.send_message(message)
                if response != "OK":
                    raise Exception("Unexpected response: " + response)

                response = self.whitePlayer.send_message(message)
                if response != "OK":
                    raise Exception("Unexpected response: " + response)

                for spec in self.spectators:
                    response = spec.send_message(message)
                    if response != "OK":
                        raise Exception("Unexpected response: " + response)

                if roll == self.blackPlayer:
                    roll = self.whitePlayer
                else:
                    roll = self.blackPlayer
            except ValueError:
                print "Error in the message"
                # rewind state to the beginning of the roll and try again
                self.set_game_status(state_backup)
                roll = roll_backup
                self.__previous_gamestate = previous_state_backup
                redice = False

    def __parse_response(self, response, roll):
        data = response.split("|")
        if data[0] == "MOVE":
            # first backup previous state
            self.__previous_gamestate = self.create_game_status_string()[1:]
            self.parse_backgammon_notation(data[1], roll)
        elif data[0] == "WRONG_MOVE":
            self.__execute_wrong_move_alert()

    def __execute_wrong_move_alert(self):
        self.set_game_status(self.__previous_gamestate)

    def parse_backgammon_notation(self, move, roll):
        """
        Parses client move data and updates board status...

        :param move: move information sent by the client such as 8/7,6/4
        :param roll: black or white Player, a Player object
        :return: None
        """
        if move == "":
            # player had no move, give the roll to the opponent
            return
        black_bar, black_off, white_bar, white_off = self.__get_bar_and_off_counts()
        for item in move.split(","):
            # check from blot hit info in the move
            blot_hit = False
            if item[-1] == "*":
                blot_hit = True
                item = item[0:-1]
                if roll == self.blackPlayer:
                    white_bar += 1
                else:
                    black_bar += 1

            source, target = item.split("/")
            source_from_bar = False
            if source == "bar":
                # checker from bar control
                source_from_bar = True
                source = 0

            target_to_off = False
            if target == "off":
                # checker to off position
                target_to_off = True
                target = 25

            source = int(source)
            target = int(target)
            if roll == self.whitePlayer:
                source = 25 - source
                target = 25 - target

            if blot_hit:
                # Let's make a blot hit first!
                self.gameStatus[target].count = 0
                self.gameStatus[target].color = ""

            if source_from_bar:
                if roll == self.blackPlayer:
                    black_bar -= 1
                else:
                    white_bar -= 1
            else:
                # decrease source point by 1
                self.gameStatus[source].count -= 1
                if self.gameStatus[source].count <= 0:
                    self.gameStatus[source].count = 0
                    self.gameStatus[source].color = ""

            if target_to_off:
                if roll == self.blackPlayer:
                    black_off += 1
                else:
                    white_bar += 1
            else:
                # increase target point by 1
                self.gameStatus[target].count += 1
                if self.gameStatus[target].count > 0:
                    if roll == self.blackPlayer:
                        self.gameStatus[target].color = "b"
                    else:
                        self.gameStatus[target].color = "w"

        self.__set_bar_and_off_counts(black_bar, black_off, white_bar, white_off)

    def __get_bar_and_off_counts(self):
        black_bar, white_bar = self.gameStatus[0].color.split("/")
        black_off, white_off = self.gameStatus[25].color.split("/")
        return int(black_bar), int(black_off), int(white_bar), int(white_off)

    def __set_bar_and_off_counts(self, black_bar, black_off, white_bar, white_off):
        self.gameStatus[0].color = "%d/%d" % (black_bar, white_bar)
        self.gameStatus[25].color = "%d/%d" % (black_off, white_off)

    def add_spectator(self, player):
        self.spectators.append(player)

    @staticmethod
    def get_new_id():
        BGGame.counterLock.acquire()
        try:
            BGGame.gameIdCounter += 1
            return "G%05d" % BGGame.gameIdCounter
        finally:
            BGGame.counterLock.release()
        pass