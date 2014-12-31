__author__ = 'Tekin.Aytekin'
import threading
import socket


class BGClient(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.__connection = socket.socket()

    def run(self):
        self.__connection.connect(("localhost", 18475))
        while 1:
            pass


# Main Module --------------------------------------------------------------------
def main():
    client = BGClient()
    client.start()

if __name__ == "__main__":
    main()