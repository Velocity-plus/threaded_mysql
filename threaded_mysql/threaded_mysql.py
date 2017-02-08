"""
Created by: Velocityplus
Github: https://github.com/Velocity-plus
"""
from listeners.tick import Repeat, Delay
from queue import Queue
import pymysql.cursors

q_sql = Queue()
q_timer = Queue()

class ThreadedMySQL:
    def __init__(self):
        # If a query is fetched an extra delay is added.
        self.fetch_delay = 0.1

        self._safe_thread_start = False
        self._gamethread = Repeat(self._queuehandler)
        self._callback = None
        self._tick_delay = 0
        self._active = False
        self.connection = None

    def execute(self, query, args=None, callback=None, data_pack=None, seconds=0.1):
        """
        :param query: The SQL query that you want to execute
        :param args: If the query have any args
        :param callback: The callback for the query
        :param data_pack: If you want to pass more to the callback than the query
        :param seconds: How long should it be queued, default: 0.1 sec
        :return:
        """
        # If callback = None assuming insert into statement
        q_sql.put([query, args, callback, 0, data_pack])
        q_timer.put(seconds)

    def fetchone(self, query, args=None, callback=None, data_pack=None, seconds=0.1):
        """
        :param query: The SQL query that you want to execute and fetch as one
        :param args: If the query have any args
        :param callback: The callback for the query
        :param data_pack: If you want to pass more to the callback than the query
        :param seconds: How long should it be queued, default: 0.1 sec
        :return:
        """
        # If callback = None assuming insert into statement
        q_sql.put([query, args, callback, 1, data_pack])
        q_timer.put(seconds)

    def fetchall(self, query, args=None, callback=None, data_pack=None, seconds=0.1):
        """
        :param query: The SQL query that you want to execute and fetch
        :param args: If the query have any args
        :param callback: The callback for the query
        :param data_pack: If you want to pass more to the callback than the query
        :param seconds: How long should it be queued, default: 0.1 sec
        :return:
        """
        # If callback = None assuming insert into statement
        q_sql.put([query, args, callback, 2, data_pack])
        q_timer.put(seconds)

    def handlequeue_start(self):
        """
        This function starts the repeater that handles the queue
        :return:
        """
        if self.connection:
            if not self._safe_thread_start:
                self._safe_thread_start = True
                self._gamethread.start(0.1)
                print('threaded_mysql: Queue handler started')
            else:
                print('threaded_mysql: Queue handler already started, use queuehandler_stop(self)')
        else:
            raise ValueError("threaded_mysql: You must connect to mysql first")

    def handlequeue_stop(self):
        """
        This function stops the repeater that handles the queue, notice that if it's not running no queries can be executed.
        :return:
        """
        self._gamethread.stop()
        self._safe_thread_start = False
        print('threaded_mysql: Queue handler already started, use queuehandler_stop(self)')

    def connect(self, host, user, password, db, charset, cursorclass=pymysql.cursors.DictCursor):
        try:
            self.connection = pymysql.connect(host=host,
                                              user=user,
                                              password=password,
                                              db=db,
                                              charset=charset,
                                              cursorclass=cursorclass)
            self.cursor = self.connection.cursor()
            print('threaded_mysql: connection was succesfully established')
        except:
            pass

    def commit(self):
        """
        Normal pymysql commit
        :return:
        """
        self.connection.commit()

    def close(self, commit_before_save=True):
        """
        Closes the mysql connection
        :param commit_before_save: should it save before closing the connection
        :return:
        """
        if commit_before_save:
            self.connection.commit()

        self.connection.close()

    def _safe_fetch(self, worker):
        data_pack = worker[4]
        func_callback = worker[2]
        data = self.cursor.fetchone()

        if data_pack:
            func_callback(data, data_pack)
        else:
            func_callback(data)

    def _safe_fetchall(self, worker):
        data_pack = worker[4]
        func_callback = worker[2]
        data = self.cursor.fetchall()
        if data_pack:
            func_callback(data, data_pack)
        else:
            func_callback(data)

    def _queuehandler(self):
        if self._tick_delay <= 0:
            if self._active:
                if q_sql.qsize() > 0:

                    try:
                        work = q_sql.get()
                        data_pack = work[4]
                        if work[3] == 0:
                            if work[1]:
                                self.cursor.execute(work[0], work[1])
                                if work[2]:
                                    if data_pack:
                                        work[2](data_pack)
                                    else:
                                        work[2]()
                            else:
                                self.cursor.execute(work[0])
                                if work[2]:
                                    if data_pack:
                                        work[2](data_pack)
                                    else:
                                        work[2]()

                        if work[3] == 1:
                            if work[1]:
                                self.cursor.execute(work[0], work[1])
                                if work[2]:
                                    Delay(self.fetch_delay, self._safe_fetch, (work,))
                            else:
                                self.cursor.execute(work[0])
                                if work[2]:
                                    Delay(self.fetch_delay, self._safe_fetch, (work,))

                        if work[3] == 2:
                            if work[1]:
                                self.cursor.execute(work[0], work[1])
                                if work[2]:
                                    Delay(self.fetch_delay, self._safe_fetchall, (work,))
                            else:
                                self.cursor.execute(work[0])
                                if work[2]:
                                    Delay(self.fetch_delay, self._safe_fetchall, (work,))
                    except:
                        pass

                self._active = False

            if q_timer.qsize() > 0:
                self._tick_delay = q_timer.get()
                self._active = True

        self._tick_delay -= 0.1

