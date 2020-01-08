# -*- coding: utf-8 -*-

import urllib3
from lxml import etree


class shuqugeSite:

    def __init__(self):
        self.requestHeaders = {
            'host': 'www.shuquge.com',
            'connection': "keep-alive",
            'cache-control': "no-cache",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6"
        }

    def matchBookContent(self, etreeHtml, bookid):

        #匹配内容

        h2 = etreeHtml.xpath(u"/html/body/div[@class='book']/div[@class='info']/h2/text()")
        if h2:
            bookname = h2[0]
        else:
            bookname = ''

        descShow = etreeHtml.xpath(u"/html/body/div[@class='book']/div[@class='info']/div[@class='intro']/text()")
        descHide = etreeHtml.xpath(u"/html/body/div[@class='book']/div[@class='info']/div[@class='intro']/span[@class='noshow']/text()")

        if(descHide):
            desc = descShow[1] + descHide[0]
        else:
            desc = descShow[1]

        info = etreeHtml.xpath(u"/html/body/div[@class='book']/div[@class='info']/div[@class='small']/span/text()")

        if info[0]:
            author = info[0][3:]
        else:
            author = ''

        if  info[1]:
            category = info[1][3:]
        else:
            category = 'default'

        if info[2]:
            state = info[2][3:]
        else:
            state = 'finish'

        if info[3]:
            words = info[3][3:]
        else:
            words = 0

        img = etreeHtml.xpath(u"/html/body/div[@class='book']/div[@class='info']/div[@class='cover']/img/@src")
        if img:
            cover = img[0]
        else:
            cover = 'empty'

        return {
            'name' : str(bookname),
            'relation_flag': bookid,
            'origin_site': 'shuquge',
            'author' : str(author),
            'category' : str(category),
            'words' : int(words),
            'state' : self.makeState(state),
            'description': str(desc),
            'cover' : str(cover)
        }



    def makeState(self, state):
        if state == '连载中':
            return 'writing'
        else:
            return 'finish'


    def matchArticleContent(self, articleDict, etreeHtml):

        #匹配内容
        html = etreeHtml

        h1 = html.xpath(u"/html/body/div[contains(@class, 'book')]/div[@class='content']/h1/text()")

        title = h1[0]

        contentList = html.xpath(u"/html/body/div[contains(@class, 'book')]/div[@class='content']/div[@id='content']/text()")

        content = ''
        if contentList:

            for p in contentList[0:-3]:
                content += '<p>' + p + '</p>'

        #进数据库
        intoMysqlParams = {
            'relation_flag': int(articleDict['article_id']),
            'parent_flag' : int(articleDict['relation_flag']),
            'origin_site': 'shuquge',
            'title': str(title),
            'content': str(content),
            'sort_weight' : int(articleDict['article_id']),
            'book_id' : articleDict['book_id']
        }
        return intoMysqlParams

    def matchArticleContentById(self, book_id, article_id):
        url = 'http://www.shuquge.com/txt/%d/%d.html' % (int(book_id), int(article_id))

        try:

            http = urllib3.PoolManager()

            response = http.request('get', url, headers=self.requestHeaders)

            if( response.status != 200 ):
                raise Exception('Error:page status not 200')

            html = response.data.lower().decode('utf-8')

            etreeHtml = etree.HTML(html)

            contentList = etreeHtml.xpath(u"/html/body/div[contains(@class, 'book')]/div[@class='content']/div[@id='content']/text()")

            return contentList[0:-3]

        except Exception as err:
            raise err