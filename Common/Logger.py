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
        self.__running = False

    def run(self):
        self.__running = True
        self.log_message("Logger starts!")
        while self.__running:
            self.__log_queue_entries()
            time.sleep(10)
        # log what is left in the queue
        self.__log_queue_entries()

    def __log_queue_entries(self):
        f = file(self.__fileName, "a")
        while not self.__queue.empty():
            item = self.__queue.get()
            f.write(item)
        f.close()

    def stop(self):
        self.log_message("Logger stops!")
        self.__running = False

    def log_message(self, message):
        formatted_message = "%s: %s%s" % (datetime.datetime.now().isoformat(" "), message, os.linesep)
        self.__queue.put(formatted_message)