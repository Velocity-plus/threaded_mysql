# ==============================================
# >> THREADED MYSQL (NO LAGS)
# ==============================================
from threaded_mysql import ThreadedMySQL
from listeners.tick import Repeat, GameThread
from messages import SayText2


TSQL =ThreadedMySQL()
TSQL.connect(host='localhost', user='root', password='123', db='test')
TSQL.handlequeue_start()

def print_out(data):
    for x in data:
        name = x['name']
        SayText2("Name: {}".format(name))

def no_lag():
    # There is about 100 names to select...
    TSQL.fetchall("SELECT name FROM players", callback=print_out)


def load():
    Timer = Repeat(no_lag)
    Timer.start(0.01)




# ==============================================
# >> NORMAL PYMYSQL (DOES LAGS)
# ==============================================

import pymysql.cursors
from listeners.tick import Repeat
from messages import SayText2

connection = pymysql.connect(host="localhost",
                                  user="root",
                                  password="123",
                                  db="test",
                                  charset="utf8",
                                  cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()




def crash():
    # There is about 100 names to select...
    cursor.execute("SELECT name FROM players")
    data = cursor.fetchall()
    for x in data:
        name = x['name']
        SayText2("Name: {}".format(name))


def load():
    Timer = Repeat(crash)
    Timer.start(0.01)





