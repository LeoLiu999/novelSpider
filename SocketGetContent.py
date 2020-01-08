# -*- coding: utf-8 -*-

import socket
import threading
import json
from shuquge import shuqugeSite


def tcplink(sock, addr):

    params = ''
    #sock.setblocking(0)

    try:
        data = sock.recv(10240)

        params = params + data.decode('utf-8')

    except BlockingIOError as err:
        #print(err)
        pass

    except Exception as err:
        print(err)
        pass

    if params == '':

        response = {
            'content' : ''
        }

    else:
        data = json.loads(params)

        try:
            data = json.loads(params)

            if( data['origin_site'] == 'shuquge'):

                shuquge = shuqugeSite()
                contentList = shuquge.matchArticleContentById(data['book_id'], data['article_id'])
                response = {
                    'content': contentList
                }

            else:
                response = {
                    'content': ''
                }

        except Exception as err:
            print(err)

            response = {
                'content': ''
            }

    sock.send(json.dumps(response).encode('utf-8'))
    sock.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind(('127.0.0.1', 16666))
s.listen(10)

while True:
    sock, addr = s.accept()
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.setDaemon(True)
    t.start()


