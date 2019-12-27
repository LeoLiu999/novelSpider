# -*- coding: utf-8 -*-

from Crawl import spider
import json
import threading
import time
import Constant as Const
from Dbmanager import Dbmanager


class BookOutQueue:


    def __init__(self):

        spiderObj = spider()
        self.booksQueue = spiderObj.booksQueue
        self.redis = spiderObj.redis

        self.threads = []
        self.maxThreadNums = Const.MAX_THREAD_NUMS

    def run(self):
        while (True):
            queue = self.outQueue();

            if not queue:
                time.sleep(1)
                continue;

            while True:

                for t in self.threads:
                    if  not t.is_alive():
                        self.threads.remove(t)

                if len(self.threads) > self.maxThreadNums:
                    time.sleep(0.5)
                    continue

                th = threading.Thread(target=self.getBook, name=None, args=(queue, ))

                self.threads.append(th)
                th.setDaemon(True)
                th.start()
                break

    def getBook(self, queue):
        if queue:

            dbmanager = Dbmanager()
            return dbmanager.addBook(params=queue)




    def outQueue(self):

        try:
            queue = self.redis.rpop(self.booksQueue)

            if not queue:
                return None

            return json.loads(queue);
        except Exception as err:
            print(err);


if __name__ == '__main__':
    #一直执行
    bookQueue = BookOutQueue()
    bookQueue.run()

