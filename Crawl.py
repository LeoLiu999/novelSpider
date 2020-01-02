# -*- coding: utf-8 -*-

import Constant as Const
import urllib3
import threading
import time
from lxml import etree
from shuquge import shuqugeSite
import redis
import json
import re
from Dbmanager import Dbmanager
from bloom_filter import BloomFilter


class spider:

    def __init__(self):

        self.maxBookid = Const.MAX_BOOKID
        self.requestHeaders = {
            'host': 'www.shuquge.com',
            'connection': "keep-alive",
            'cache-control': "no-cache",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6"
        }

        self.threads = []

        self.delay = Const.DELAY

        self.maxThreadNums = Const.MAX_THREAD_NUMS
        try:

            redisPool = redis.ConnectionPool(host=Const.REDIS_HOST, port=Const.REDIS_PORT)

            self.redis = redis.Redis(connection_pool=redisPool)

        except Exception as err:
            print(err)

        self.booksQueue = 'books_detail_queue'

        self.articlesQueue = 'articles_url_queue'

        self.articleHrefBloom = BloomFilter(1024 * 1024 * 16, 0.01)


    def run(self):

        bookid = 1
        while(True):

            if ( bookid > self.maxBookid ):
                break

            while(True):

                for thread in self.threads:
                    if  not thread.is_alive():
                        self.threads.remove(thread)

                if ( len(self.threads ) > self.maxThreadNums ):
                    time.sleep(self.delay)
                    continue

                try:
                    th = threading.Thread(target=self.getPageContent, name= None, args=(bookid, ))

                    self.threads.append(th)

                    th.setDaemon(True)

                    th.start()

                    time.sleep(self.delay)

                    break
                except Exception as err:
                    print(err)

            bookid = bookid + 1


    def getPageContent(self, bookid, site='shuquge'):


        try:
            if( site == 'shuquge' ):
                url  = 'http://www.shuquge.com/txt/%d/index.html' % (bookid)

            else:
                print('Error:site unkown')
                return

            bookContent = self.doRequest(url)

            etreeHtml = etree.HTML(bookContent)

            relationId = self.getBookContentIntoMysql(etreeHtml, bookid, site)

            if relationId:
                self.getBookArticleHrefsIntoRedis(etreeHtml, bookid, site, relationId)

        except Exception as err:
            print(err, 'bookid:',bookid)


    def doRequest(self, url):

        try:

            http = urllib3.PoolManager()

            response = http.request('get', url, headers=self.requestHeaders)

            if( response.status != 200 ):
                raise Exception('Error:page status not 200')

            return response.data.lower().decode('utf-8')

        except Exception as err:

            raise err





    def getBookContent(self, etreeHtml, bookid, site):

        if( site == 'shuquge' ):
            shuqugeObj = shuqugeSite()
            return shuqugeObj.matchBookContent(etreeHtml, bookid)
        else:
            return None

    def getBookContentIntoRedis(self, etreeHtml, bookid, site):
        params = self.getBookContent(etreeHtml, bookid, site)
        if params is not None:
            self.redis.lpush(self.booksQueue, json.dumps(params) )
            #print("site:%s bookid:%s into bookqueue" % (site, bookid) )

    def getBookContentIntoMysql(self, etreeHtml, bookid, site):
        params = self.getBookContent(etreeHtml, bookid, site)
        if params is not None:
            dbmanager = Dbmanager()
            return dbmanager.addBook(params=params)


    def getBookArticleHrefsIntoRedis(self, etreeHtml, bookid, site, relationId):

        if (site == 'shuquge'):
            db = Dbmanager()
            maxId = db.getMaxArticleRelationFlag(parentFlag=bookid, originSite=site)

            hrefs = etreeHtml.xpath(u"/html/body/div[@class='listmain']/dl/dd/a[@href]")

            if hrefs is not None:
                for href in hrefs:
                    link = href.attrib['href']

                    matchs = re.match('(\d+).html', link)

                    if not matchs:
                        continue

                    article_id = int(matchs.group(1))
                    if article_id <= maxId:
                        continue

                    self.articleHrefIntoRedis(bookid, article_id, link, site, relationId)

        else:
            return None

    def articleHrefIntoRedis(self, bookid, article_id, link, site, relationId):

        key = "%s:%s" % (bookid, article_id)

        if key not in self.articleHrefBloom:

            params = {
                'url': link,
                'site': site,
                'relation_flag': bookid,
                'article_id': article_id,
                'book_id' : relationId
            }
            self.redis.lpush(self.articlesQueue, json.dumps(params))

            self.articleHrefBloom.add(key)

        #print("site:%s bookid:%s link:%s into articlequeue" % (site, bookid, link))


if __name__ == '__main__':
    #几个小时执行一次
    spider = spider();
    spider.run();
