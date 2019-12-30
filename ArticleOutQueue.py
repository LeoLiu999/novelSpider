# -*- coding: utf-8 -*-

from Crawl import spider
import json
import threading
import time
import Constant as Const
from Dbmanager import Dbmanager
import urllib3
from lxml import etree
from shuquge import shuqugeSite

class ArticleOutQueue:


    def __init__(self):

        spiderObj = spider()
        self.articleQueue = spiderObj.articlesQueue
        self.redis = spiderObj.redis

        self.threads = []
        self.maxThreadNums = Const.MAX_THREAD_NUMS

        self.delay = Const.DELAY

        self.requestHeaders = {
            'host': 'www.shuquge.com',
            'connection': "keep-alive",
            'cache-control': "no-cache",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6"
        }

    def run(self):
        while (True):
            queue = self.outQueue();

            if not queue:

                time.sleep(self.delay)
                continue;

            while True:

                for t in self.threads:
                    if  not t.is_alive():
                        self.threads.remove(t)

                if len(self.threads) > self.maxThreadNums:
                    time.sleep(self.delay)
                    continue

                th = threading.Thread(target=self.getArticle, name=None, args=(queue, ))

                self.threads.append(th)
                th.setDaemon(True)
                th.start()
                time.sleep(self.delay)
                break

    def getArticle(self, queue):
        if list:

            try:
                self.requestGetArticleIntoMysql(queue)


            except Exception as err:
                print(err)
            #dbmanager = Dbmanager()
            #return dbmanager.addBook(params=list)


    def requestGetArticleIntoMysql(self, queue):


        article = self.requestGetArticle(queue)

        if article:
            return self.intoMysql(article)
        else:
            return None

    def requestGetArticle(self,queue):
        if( queue['site'] == 'shuquge' ):
            url = 'http://www.shuquge.com/txt/%s/%s.html' % (queue['relation_flag'], queue['article_id'] )
        else:
            return None

        try:
            content = self.request(url)

            if (queue['site'] == 'shuquge'):
                etreeHtml = etree.HTML(content)
                shuquge = shuqugeSite()
                return shuquge.matchArticleContent(articleDict = queue, etreeHtml = etreeHtml)
            else:
                return None
        except Exception as err:
            raise err

    def request(self, url):
        try:

            http = urllib3.PoolManager()

            r = http.request('get', url, headers=self.requestHeaders)

            if (r.status != 200):
                raise Exception('Error:page status not 200')

            content = r.data

            return content.lower().decode('utf-8')

        except IOError as err:
            raise err
        except Exception as err:
            raise err

    def intoMysql(self, article):
        db = Dbmanager()
        return  db.addArticle(params=article)
        pass

    def outQueue(self):

        try:
            queue = self.redis.rpop(self.articleQueue)

            if not queue:
                return None

            return json.loads(queue);
        except Exception as err:
            print(err);


if __name__ == '__main__':
    #一直执行
    article = ArticleOutQueue()
    article.run()

