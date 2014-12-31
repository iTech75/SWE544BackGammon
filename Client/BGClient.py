__author__ = 'Tekin.Aytekin'
import threading
import socket
import string
import sys


class BGClient(threading.Thread):
    __gameStatus = []

    def __init__(self):
        threading.Thread.__init__(self)

        self.__connection = socket.socket()
        self.__gameStatus = [""] * 26
        self.__gameStatus[0] = "0"
        self.__gameStatus[25] = "0"

    def run(self):
        # self.__connection.connect(("localhost", 18475))
        self.draw("1w2|6b5|8b3|12w5|12b5|17w3|19w5|24b2")
        while 1:
            pass

    def draw(self, game_state):
        print "544 BG Client"
        _buffer = game_state.split('|')
        for i in range(len(_buffer)):
            checker_color = "b"
            buffer2 = _buffer[i].split(checker_color)

            if len(buffer2) == 1:
                checker_color = "w"
                buffer2 = _buffer[i].split(checker_color)

            if buffer2.__len__() == 2:
                self.__gameStatus[int(buffer2[0])] = checker_color + buffer2[1]

        print "  |13 14 15 16 17 18 || 19 20 21 22 23 24|"
        print "------------------------------------------"
        for line in range(15):
            print string.ascii_uppercase[line] + ".|                  ||                  |"
        print "------------------------------------------"
        print "  |12 11 10 09 08 07 || 06 05 04 03 02 01|"
        print "Have a gg"


# Main Module --------------------------------------------------------------------
def main():
    client = BGClient()
    client.start()

if __name__ == "__main__":
    main()