__author__ = 'Tekin.Aytekin'
import threading
import Queue
import datetime
import time
import os


class Logger (threading.Thread):

    def __init__(self, filename, queue):
        assert isinstance(filename, str)
        assert isinstance(queue, Queue.Queue)

        threading.Thread.__init__(self)
        self.__fileName = filename
        self.__queue = queue

    def run(self):
        running = True
        while running:
            f = file(self.__fileName, "a")
            while not self.__queue.empty():
                item = self.__queue.get()
                f.write(item)
            f.close()
            time.sleep(10)

    def log_message(self, message):
        formatted_message = "%s: %s%s" % (datetime.datetime.now().isoformat(" "), message, os.linesep)
        self.__queue.put(formatted_message)