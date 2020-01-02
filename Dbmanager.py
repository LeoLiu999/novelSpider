# -*- coding: utf-8 -*-

import mysql.connector
import Constant
from DownloadImage import DownloadImage
import time

class Dbmanager:

    def __init__(self):

        self.dbconfig = {
            'host' : Constant.MYSQL_HOST,
            'user' : Constant.MYSQL_USER,
            'password' : Constant.MYSQL_PASSWORD,
            'database' : Constant.MYSQL_DB
        }
        self.maxThreadNum = Constant.MAX_THREAD_NUMS + 3

        self.categories = {
                '玄幻奇幻': 1,
                '玄幻魔法': 1,
                '武侠修真': 2,
                '历史军事': 3,
                '都市言情': 4,
                '科幻灵异': 5,
                '侦探推理': 6,
                '恐怖悬疑': 6,
                '网游动漫': 7,
                '其他类型': 8,
                'default': 8
            }
        try:

            self.connector = mysql.connector.connect(pool_name='mypool', pool_size=self.maxThreadNum, **self.dbconfig)
            self.cursor = self.connector.cursor()
        except mysql.connector.Error as err:
            print(err)
            exit(1)


    def addBook(self, params):

        try:

            sql = "SELECT * FROM `books` WHERE relation_flag = %s and origin_site = %s LIMIT 1"
            vals = (params['relation_flag'], params['origin_site'])
            self.cursor.execute(sql, vals)

            one  = self.cursor.fetchone()

            if one:
                sql = "UPDATE `books` SET words = %s,update_time = %s,state=%s where relation_flag = %s and origin_site = %s";
                values = (
                    params['words'],
                    int(time.time()),
                    params['state'],
                    params['relation_flag'],
                    params['origin_site'],
                )
                self.cursor.execute(sql, values)
                self.connector.commit()
                return one[0]
            else:
                do = DownloadImage()
                cover = do.download(params['cover'])

                if cover is None:
                    cover = '/cover/default.png'



                sql = "INSERT INTO `books`(`name`,`relation_flag`,`origin_site`,`author`,`category`,`category_id` ,`words`,`state`,`description`,`cover`,`create_time`)" \
                      " VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                values = (
                        params['name'],
                        params['relation_flag'],
                        params['origin_site'],
                        params['author'],
                        self.formatCategory( params['category'] ),
                        self.getCategoryId(params['category']),
                        params['words'],
                        params['state'],
                        params['description'],
                        cover,
                        int(time.time())
                )

                self.cursor.execute(sql, values)
                self.connector.commit()

                return self.cursor.lastrowid

        except mysql.connector.Error as err:
            print('dbmanager:mysqlerror:',err)
            return
        except Exception as err:
            print('dbmanager:error:',err)
            return
        finally:
            self.cursor.close()
            self.connector.close()

    def getCategoryId(self, categoryName):

        try:
            return self.categories[categoryName]
        except Exception as err:
            return  self.categories['default']

    def formatCategory(self, category):
        if category == '玄幻魔法':
            return '玄幻奇幻'
        elif category == '侦探推理':
            return '恐怖悬疑'
        else:
            return category

    def addArticle(self, params):

        try:



            book_id = params['book_id']

            hash_id = int(book_id) % 30
            tableName = 'articles_%d' % (hash_id, )

            sql ="INSERT INTO " +tableName+ "(`book_id`, `relation_flag`,`parent_flag`,`origin_site`,`title`,`content`,`sort_weight`,`create_time`) VALUES(%s, %s,%s,%s,%s,%s,%s,%s)"
            values = (
                        book_id,
                        params['relation_flag'], params['parent_flag'], params['origin_site'],
                        params['title'], params['content'], params['sort_weight'],
                        int(time.time())
                      )

            self.cursor.execute(sql, values)
            self.connector.commit()

            sql = "UPDATE `books` SET update_article_time = %s where id = %s";
            values = (

                int(time.time()),
                book_id
            )
            self.cursor.execute(sql, values)
            self.connector.commit()


        except mysql.connector.Error as err:
            print(err)
            exit(1)
        except Exception as err:
            print('error:',err)
            exit(1)
        finally:
            self.cursor.close()
            self.connector.close()

    def getMaxArticleRelationFlag(self, parentFlag, originSite):

        try:
            book_id = parentFlag

            hash_id = int(book_id) % 30
            tableName = 'articles_%d' % (hash_id,)

            sql = "SELECT max(`relation_flag`) as max_relation_flag FROM "+tableName+" WHERE parent_flag = %s and origin_site = %s LIMIT 1"
            vals = (parentFlag, originSite)
            self.cursor.execute(sql, vals)

            one = self.cursor.fetchone()

            if one[0]:
                return int(one[0])
            else:
                return 0
        except mysql.connector.Error as err:
            print(err)
            exit(1)
        except Exception as err:
            print('error:', err)
            exit(1)
        finally:
            self.cursor.close()
            self.connector.close()