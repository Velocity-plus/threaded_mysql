from messages import SayText2
from threaded_mysql import ThreadedMySQL
import pymysql.cursors

# ON = No lag | OFF = Server freeze
use_threaded_mysql = 1

connection = pymysql.connect(host="localhost",
                                  user="root",
                                  password="123pass",
                                  db="trikz_server",
                                  charset="utf8",
                                  cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()


def load():
    # Put use_threaded_mysql = 1 to test the difference
    if not use_threaded_mysql:

        # Executes the query 1000 times
        for x in range(1000):

            cursor.execute('SELECT name FROM stats')
            data = cursor.fetchone()
            # Prints it out (not necessary tho)
            SayText2('Name: {}'.format(data['name'])).send()
    else:
        # Class
        TSQL = ThreadedMySQL()
        # Use the connection already created
        TSQL.connect_use(connection)
        # Starts the queuehandler
        TSQL.handlequeue_start()

        TSQL.fetchone('SELECT name FROM lol', callback=test)


def test(data):
    SayText2('Name: {}'.format(data['name'])).send()


