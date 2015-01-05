__author__ = 'Tekin.Aytekin'
import threading
import socket
import string
import colorama


class BGClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.__connection = socket.socket()
        self.__gameStatus = [""] * 26
        self.__gameStatus[0] = "0"
        self.__gameStatus[25] = "0"
        self.__screenBuffer = [["" for x in range(60)] for xx in range(19)]
        self.__opponentName = "None"
        self.__user_name = "None"
        self.__color = ""

    def run(self):
        self.__user_name = raw_input("Please enter your username > ")
        self.__connection.connect(("localhost", 18475))
        self.__connection.send("CONNECT|" + self.__user_name)
        response = self.__connection.recv(1024)
        if response == "OK":
            running = True
            while running:
                user_choice = self.__show_menu()
                if user_choice == "1":
                    self.__start_game()
                if user_choice == "2":
                    self.__watch_game()
        else:
            print "Cannot connect to the server, reason: " + response
            self.__connection.close()

    def __start_game(self):
        game_state = "0/0|1w2|6b5|8b3|12w5|13b5|17w3|19w5|24b2|0/0"
        self.__connection.send("PLAY")
        response = self.__connection.recv(1024)
        if self.__parse_response(response, game_state)[0] == "OK":
            # game started, wait for server
            gaming = True

            black_player = self.__user_name
            white_player = self.__opponentName
            if self.__color == "w":
                black_player = self.__opponentName
                white_player = self.__user_name

            self.draw(game_state, black_player, white_player)
            while gaming:
                request = self.__connection.recv(1024)
                response, game_state = self.__parse_response(request, game_state)
                self.draw(game_state, black_player, white_player)
                if not (self.end_game_control(response)):
                    self.__connection.send(response)
                else:
                    self.__connection.send("OK")  # to make server go on
                    gaming = False

            print ""
            raw_input("Press enter to continue")

        elif self.__parse_response(response, game_state)[0] == "NOOPPONENT":
            print "Exceeded time to find an opponent, server is deserted at the moment!"
        else:
            print "Unknown response from the server: %s" % self.__parse_response(response, game_state)[0]

    @staticmethod
    def end_game_control(response):
        if response.startswith("YOUWIN"):
            print "************************************"
            print "************************************"
            print "W I N N W E R"
            print "************************************"
            print "Congratz"
            print "************************************"
            return True
        elif response.startswith( "YOULOSE"):
            print "************************************"
            print "************************************"
            print "L O S E R"
            print "************************************"
            print "Next time"
            print "************************************"
            return True
        elif response.startswith("WINNER"):
            commands = response.split("|")
            print "************************************"
            print "************************************"
            print "%s WINS the game..." % commands[1]
            print "************************************"
            print "************************************"
            return True
        else:
            return False

    def __watch_game(self):
        game_state = "0/0|1w2|6b5|8b3|12w5|13b5|17w3|19w5|24b2|0/0"
        self.__connection.send("WATCH")
        response = self.__connection.recv(1024)
        if self.__parse_response(response, game_state)[0] == "OK":
            # game started, wait for server
            gaming = True
            command, game_id, black, white = response.split("|")
            self.__connection.send("GETSTATUS|%s" % game_id)
            response = self.__connection.recv(1024)
            response, game_state = self.__parse_response(response, game_state)
            self.draw(game_state, black, white)
            while gaming:
                request = self.__connection.recv(1024)
                response, game_state = self.__parse_response(request, game_state)
                self.draw(game_state, black, white)
                if not (self.end_game_control(response)):
                    self.__connection.send(response)
                else:
                    self.__connection.send("OK")  # to make server go on
                    gaming = False
            print ""
            raw_input("Press enter to continue")

    def __parse_response(self, response, game_status):
        data = response.split("|")
        if data[0] == "OPPONENT":
            self.__opponentName = data[1]
            self.__color = data[2]
            return "OK", game_status
        elif data[0] == "NOOPPONENT":
            return "NOOPPONENT", game_status
        elif data[0] == "YOURTURN":
            return self.make_move(data[1]), game_status
        elif data[0] == "SETSTATUS":
            return "OK", "|".join(data[1:])
        elif data[0] == "ID":
            return "OK", game_status
        elif data[0] == "STATUS":
            return "OK", "|".join(data[1:])
        elif data[0] == "YOUWIN":
            return "YOUWIN", "|".join(data[1:])
        elif data[0] == "YOULOSE":
            return "YOULOSE", "|".join(data[1:])
        elif data[0] == "WINNER":
            return response, "|".join(data[2:])
        elif data[0] == "ERRORINCOMMAND":
            return "ERRORINCOMMAND", game_status
        else:
            return "ERRORINCOMMAND", game_status

    @staticmethod
    def make_move(dice):
        move = raw_input("Please make your move, dice is %s:" % dice)
        if move == "W" or move == "WRONG" or move == "WRONG_MOVE":
            return "WRONG_MOVE"
        elif move == "WITHDRAW" or move == "-":
            return "WITHDRAW"
        else:
            return "MOVE|%s" % move

    @staticmethod
    def __show_menu():
        print "-------------------------"
        print "1. PLAY a game"
        print "2. WATCH a game"
        print "3. DISCONNECT from server"
        print "-------------------------"
        return raw_input("Please make your choice (1,2,3) > ")

    def draw(self, game_state, black_player_name, white_player_name):
        """
        Draws game to the console screen, uses a screen buffer to accompalish the task
        :param game_state: state to be drawn on the screen
        :return: none
        """
        print "544 BG Client"
        print "-------------"
        _buffer = game_state.split('|')
        black_bar, white_bar = _buffer[0].split("/")
        black_off, white_off = _buffer[len(_buffer) - 1].split("/")
        _buffer.remove(_buffer[0])
        _buffer.remove(_buffer[len(_buffer) - 1])

        for i in range(1, 25):
            self.__gameStatus[i] = ""

        for i in range(len(_buffer)):
            checker_color = "b"
            buffer2 = _buffer[i].split(checker_color)

            if len(buffer2) == 1:
                checker_color = "w"
                buffer2 = _buffer[i].split(checker_color)

            if buffer2.__len__() == 2:
                self.__gameStatus[int(buffer2[0])] = checker_color + buffer2[1]
            else:
                self.__gameStatus[int(buffer2[0])] = ""

        if self.__color == "b":
            self.write_to_screen_buffer(0, "  |13 14 15 16 17 18 || 19 20 21 22 23 24|")
        else:
            self.write_to_screen_buffer(0, "  |12 11 10 09 08 07 || 06 05 04 03 02 01|")
        self.write_to_screen_buffer(1, "------------------------------------------")
        for line in range(15):
            self.write_to_screen_buffer(line + 2, string.ascii_uppercase[line] +
                                        ".|                  ||                  |")
        self.write_to_screen_buffer(17, "------------------------------------------")
        if self.__color == "b":
            self.write_to_screen_buffer(18, "  |12 11 10 09 08 07 || 06 05 04 03 02 01|")
        else:
            self.write_to_screen_buffer(18, "  |13 14 15 16 17 18 || 19 20 21 22 23 24|")

        for i in range(1, 25):
            if self.__gameStatus[i] != "":
                checker_color = self.__gameStatus[i][0]
                if checker_color == "w":
                    checker_color = "O"
                else:
                    checker_color = "*"

                checker_count = int(self.__gameStatus[i][1:])
                for j in range(checker_count):
                    if i < 13:
                        row = 16 - j
                        column = 42 - (i * 3)
                        if i > 6:
                            column -= 3
                        self.__screenBuffer[row][column] = checker_color
                    else:
                        row = 2 + j
                        column = ((i - 12) * 3)
                        if i > 18:
                            column += 3
                        self.__screenBuffer[row][column] = checker_color

        self.write_to_screen_buffer_xy(2, 43, "O_Bar:%s" % white_bar)
        self.write_to_screen_buffer_xy(3, 43, "O_Col:%s" % white_off)
        self.write_to_screen_buffer_xy(4, 43, white_player_name)
        self.write_to_screen_buffer_xy(14, 43, black_player_name)
        self.write_to_screen_buffer_xy(15, 43, "*_Col:%s" % black_off)
        self.write_to_screen_buffer_xy(16, 43, "*_Bar:%s" % black_bar)
        for i in range(0, 19):
            print "".join(self.__screenBuffer[i])

    def write_to_screen_buffer(self, index, value):
        for i in range(len(value)):
            self.__screenBuffer[index][i] = value[i]

    def write_to_screen_buffer_xy(self, row, column, value):
        for i in range(column, column + len(value)):
            self.__screenBuffer[row][i] = value[i - column]


# Main Module --------------------------------------------------------------------
def main():
    colorama.init()
    client = BGClient()
    client.start()

if __name__ == "__main__":
    main()