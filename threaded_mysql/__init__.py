"""
Created By Velocity-plus
Github: https://github.com/Velocity-plus/
"""
from listeners.tick import GameThread
from queue import Queue
from time import time as timestamp, sleep
import pymysql.cursors


class ThreadedMySQL:

    def __init__(self):
        # Is the thread running?
        self.thread_status = False
        # Regular Queue
        self._r_queue = Queue()
        # Prioitized Queue
        self._p_queue = Queue()

        self.connection_method = 0

        # Show print messages?
        self._debug = True

        self.wait = 0

    def wait(self, delay):
        """
        If you for some reason want to delay the queue
        :param delay: The delay in seconds
        :return:
        """
        self.wait = delay

    def execute(self, query, args=None, callback=None, data_pack=None, prioritize=False, get_info=False):
        """
            This function cannot pass fetched data to the callback!
        :param query: The SQL query that you want to execute
        :param args: If the SQL query have any args
        :param callback: The callback for the query
        :param data_pack: If you want to pass special information to the callback
        :param prioritize: If you have large queues, prioritizing the query can make it skip the queue
         before the rest of the queue is finished
        :param get_info: If you want information about the query passed to the callback
         (such as timestamp, query and prioritized)
        :return:
        """
        # We need this later
        query_type = 0

        # If callback = None assuming no data returned needed
        if get_info:
            get_info = {'query': query, 'time': timestamp(), 'prioritized': prioritize}

        if not prioritize:
            self._r_queue.put([query, args, callback, data_pack, get_info, query_type])
        else:
            self._p_queue.put([query, args, callback, data_pack, get_info, query_type])

    def fetchone(self, query, args=None, callback=None, data_pack=None, prioritize=False, get_info=False):
        """
            This function both execute and fetch data, no need to execute before using this!
        :param query: The SQL query that you want to execute
        :param args: If the SQL query have any args
        :param callback: The callback for the query
        :param data_pack: If you want to pass special information to the callback
        :param prioritize: If you have large queues, prioritizing the query can make it skip the queue
         before the rest of the queue is finished
        :param get_info: If you want information about the query passed to the callback
         (such as timestamp, query and prioritized)
        :return:
        """
        query_type = 1
        if get_info:
            get_info = {'query': query, 'time': timestamp(), 'prioritized': prioritize}

         # If callback = None assuming no data returned needed
        if not prioritize:
            self._r_queue.put([query, args, callback, data_pack, get_info, query_type])
        else:
            self._p_queue.put([query, args, callback, data_pack, get_info, query_type])

    def fetchall(self, query, args=None, callback=None, data_pack=None, prioritize=False, get_info=False):
        """
          This function both execute and fetch data, no need to execute before using this!
        :param query: The SQL query that you want to execute
        :param args: If the SQL query have any args
        :param callback: The callback for the query
        :param data_pack: If you want to pass special information to the callback
        :param prioritize: If you have large queues, prioritizing the query can make it skip the queue
         before the rest of the queue is finished
        :param get_info: If you want information about the query passed to the callback
         (such as timestamp, query and prioritized)
        :return:
        """
        query_type = 2

        if get_info:
            get_info = {'query': query, 'time': timestamp(), 'prioritized': prioritize}

        # If callback = None assuming no data returned needed
        if not prioritize:
            self._r_queue.put([query, args, callback, data_pack, get_info, query_type])
        else:
            self._p_queue.put([query, args, callback, data_pack, get_info, query_type])

    def complete_task(self, worker, prio=None):
        query = worker[0]
        args = worker[1]
        callback = worker[2]
        data_pack = worker[3]
        get_info = worker[4]
        query_type = worker[5]
        try:
            if get_info:
                get_info['time'] = timestamp() - get_info['time']

            if args:
                self.cursor.execute(query, args)
            else:
                self.cursor.execute(query)

            if query_type == 0:
                if get_info:
                    if callback:
                        if data_pack:
                            callback(data_pack, get_info)
                        else:
                            callback(get_info)
                else:
                    if callback:
                        if data_pack:
                            callback(data_pack)
                        else:
                            callback()
            if query_type == 1:
                data = self.cursor.fetchone()
                if get_info:
                    if callback:
                        if data_pack:
                            callback(data, data_pack, get_info)
                        else:
                            callback(data, get_info)
                else:
                    if callback:
                        if data_pack:
                            callback(data, data_pack)
                        else:
                            callback(data)

            if query_type == 2:
                data = self.cursor.fetchall()
                if get_info:
                    if callback:
                        if data_pack:
                            callback(data, data_pack, get_info)
                        else:
                            callback(data, get_info)
                else:
                    if callback:
                        if data_pack:
                            callback(data, data_pack)
                        else:
                            callback(data)
            if prio:
                self._p_queue.task_done()
            else:
                self._r_queue.task_done()

        except Exception as SQL_ERROR:
            # Possible errors
            retryExceptions = tuple([
                pymysql.InternalError,
                pymysql.OperationalError,
                pymysql.Error,
            ])

            ie, oe, e = retryExceptions
            print('-'*64)

            print('Exceptions Found: (SQL Query: {})'.format(query))
            if ie:
                print(' * threaded_mysql: [ERROR] Exception pymysql.InternalError')
            if oe:
                print(' * threaded_mysql: [ERROR] Exception pymysql.OperationalError')
            if e:
                print(' * threaded_mysql: [ERROR] Exception pymysql.Error')
            print('Actual Error:')
            print(' * threaded_mysql: {}'.format(SQL_ERROR.args))
            print('-' * 64)

    def _threader(self):
        while self.thread_status:
            if self.wait:
                sleep(self.wait)

            if self._p_queue.empty():
                worker = self._r_queue.get()
                self.complete_task(worker, prio=False)

            else:
                worker = self._p_queue.get()
                self.complete_task(worker, prio=True)

    def _start_thread(self):
        # Creates the thread
        self.t = GameThread(target=self._threader)
        self.t.daemon = True
        self.t.start()

    def handlequeue_start(self):
        """
        This handles the queue, should be stopped on unload
        :return:
        """
        # Starts the queue
        self.thread_status = True # This must be true before the thread can loop
        self._start_thread()

    def handlequeue_stop(self):
        """
        This stops the queue for being processed, while a connection still might be open
         no queries can be executed.
        :return:
        """
        self.thread_status = False

    def queue_size(self):
        """
        :return: Returns the size of the queue
        """
        return self._r_queue.qsize() + self._p_queue.qsize()

    def connect(self, host, user, password, db, charset, cursorclass=pymysql.cursors.DictCursor):
        """
        Checkout PyMYSQL documentation for complete walkthrough
        """
        try:
            self.connection = pymysql.connect(host=host,
                                              user=user,
                                              password=password,
                                              db=db,
                                              charset=charset,
                                              cursorclass=cursorclass)
            self.cursor = self.connection.cursor()
            if self._debug:
                print('threaded_mysql: [SUCCES] connection was succesfully established.')

            self.connection_method = 1
        except:
            if self._debug:
                print('threaded_mysql: [ERROR] Not possible to make a connection.')

    def connect_use(self, connection):
        """
        If you created your connection elsewhere in your code, you can pass it to Threaded MySQL
        :param connection: Your connection socket
        :return:
        """
        try:
            self.connection = connection
            self.cursor = self.connection.cursor()
            if self._debug:
                print('threaded_mysql: [SUCCES] Cursor created succesfully for your connection.')
            self.connection_method = 2
        except:
            if self._debug:
                print('threaded_mysql: [ERROR] Not possible to create cursor.')

    def commit(self):
        """
        Regular pymysql commit
        :return:
        """
        self.connection.commit()

    def close(self, finish_queue_before_close=False):
        """
        Closes the mysql connection
        :param finish_queue_before_close: Finishes the queue before it terminates the connection
        :return:
        """
        if finish_queue_before_close:
            while self.queue_size() > 0:
                pass
            else:
                self.connection.close()
        else: self.connection.close()