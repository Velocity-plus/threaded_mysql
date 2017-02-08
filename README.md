**Threaded MySQL**
-------------
----------
Tired of lag?

If your server requires a remote connection to a database, stacked up queries can cause noticeable lag in your game server (freezing, players twitching) since MySQL doesn't 'really' queue up the queries. 

I've made a library to fix this problem, it basically queues up the queries and executes them after a certain delay (that can be modified).
 It's inspired from the Sourcemod threaded MySQL https://wiki.alliedmods.net/SQL_(SourceMod_Scripting) Remember that all queries now requires a callback, since they are dispatched.

**The library**
***threaded_mysql.py***

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
            


**Documentation**
-------------
----------

The library works as an extension of PyMYSQL, so as any other MySQL script, a connection must be established to a database, but before we can do that, let us initialize the class for threaded MySQL. 

    from threaded_mysql import ThreadedMySQL
    
    TSQL = ThreadedMySQL()

After we have initialized our class, we can connect to our MySQL database (in future updates, you can create the connection elsewhere and pass it into the class, but for now..).

    Available paramenters (host, user, password, db ,charset, cursorclass)
    TSQL.connect(host='localhost', user='root', password='123', db='utf8')

Now that our connection has been made, we need to start the thread that handles the queue of queries, as seen below.

    TSQL.handlequeue_start()

Finally, now we can make use of it. The functions available are listed below

    TSQL.execute(query, args=None, callback=None, data_pack=None, seconds=0.1)
    TSQL.fetchone(query, args=None, callback=None, data_pack=None, seconds=0.1)
    TSQL.fetchall(query, args=None, callback=None, data_pack=None, seconds=0.1)

It's important to note that when using the **fetchone** or **fetchall** it will execute the query BEFORE fetching it, so no need to use TSQL.execute when you want to fetch something.

If you want to grab the data from **fetchone** or **strong text**fetchall a callback is necessary. To demonstrate this look at the code examples below:

**Code examples**
-------------


----------


    from messages import SayText2
    from events import Event
    from threaded_mysql import ThreadedMySQL
    
    # Initializes the class
    TSQL = ThreadedMySQL()
    
    # Connects to a mysql database
    TSQL.connect('localhost','root','123','datbase_example','utf8')
    
    # Starts the queuehandler (should only be called once)
    TSQL.handlequeue_start()
    
    # The callback 
    def sql_callback(data):
        print(data)
    
    # The callback 
    def sql_callback_2(data, data_pack):
        text = data_pack['text']
        print(data)
        print("You wrote {0}".format(text))
    
    
    @Event('player_say')
    def on_player_say(game_event):
            # What did the player write
            text = game_event['text']
       
            if text == '!fetchall':
                # Fetches all the names 
                TSQL.fetchall('SELECT name FROM database_example', callback=sql_callback)
    
            if text == '!fetchone':
                 # Let's pass some extra things...
                 data_pack = {'text':text}
                 # Fetches one name
                 TSQL.fetchall('SELECT name FROM database_example', callback=sql_callback_2, data_pack=data_pack)


> Output !fetchall
> =>  [{'name': John'}, {'name': 'Daniel'}.... 
> 
> Output !fectone
> =>  ['name': John']
> => You wrote !fetchone



You can even create tick listener and spam queries without any lag at all

Enjoy :)
