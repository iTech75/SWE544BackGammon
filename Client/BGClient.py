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
        else:
            print "Cannot connect to the server, reason: " + response
            self.__connection.close()

    def __start_game(self):
        game_state = "1w2|6b5|8b3|12w5|13b5|17w3|19w5|24b2"
        self.__connection.send("PLAY")
        response = self.__connection.recv(1024)
        if self.__parse_response(response, game_state) == "OK":
            # game started, wait for server
            gaming = True
            while gaming:
                self.draw(game_state)
                request = self.__connection.recv(1024)
                response = self.__parse_response(request, game_state)
                self.__connection.send(response)

    def __parse_response(self, response, game_status):
        data = response.split("|")
        if data[0] == "OPPONENT":
            self.__opponentName = data[1]
            return "OK"
        elif data[0] == "NOOPPONENT":
            pass
        elif data[0] == "YOURTURN":
            return self.make_move(data[1])
        elif data[0] == "SETSTATUS":
            game_status = data[1]
            return "OK"
        else:
            pass

    @staticmethod
    def make_move(dice):
        move = raw_input("Please make your move, dice is %s:" % dice)
        return "MOVE|%s" % move

    @staticmethod
    def __show_menu():
        print "-------------------------"
        print "1. PLAY a game"
        print "2. WATCH a game"
        print "3. DISCONNECT from server"
        print "-------------------------"
        return raw_input("Plaese make your choice (1,2,3) > ")

    def draw(self, game_state):
        """
        Draws game to the console screen, uses a screen buffer to accompalish the task
        :param game_state: state to be drawn on the screen
        :return: none
        """
        print "544 BG Client"
        print "-------------"
        _buffer = game_state.split('|')
        for i in range(len(_buffer)):
            checker_color = "b"
            buffer2 = _buffer[i].split(checker_color)

            if len(buffer2) == 1:
                checker_color = "w"
                buffer2 = _buffer[i].split(checker_color)

            if buffer2.__len__() == 2:
                self.__gameStatus[int(buffer2[0])] = checker_color + buffer2[1]

        self.write_to_screen_buffer(0, "  |13 14 15 16 17 18 || 19 20 21 22 23 24|")
        self.write_to_screen_buffer(1, "------------------------------------------")
        for line in range(15):
            self.write_to_screen_buffer(line + 2, string.ascii_uppercase[line] +
                                        ".|                  ||                  |")
        self.write_to_screen_buffer(17, "------------------------------------------")
        self.write_to_screen_buffer(18, "  |12 11 10 09 08 07 || 06 05 04 03 02 01|")

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

        self.write_to_screen_buffer_xy(2, 43, "O_Bar:0")
        self.write_to_screen_buffer_xy(3, 43, "O_Col:0")
        self.write_to_screen_buffer_xy(4, 43, self.__opponentName)
        self.write_to_screen_buffer_xy(14, 43, self.__user_name)
        self.write_to_screen_buffer_xy(15, 43, "*_Col:0")
        self.write_to_screen_buffer_xy(16, 43, "*_Bar:0")
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