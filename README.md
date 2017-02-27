Threaded MySQL
===================== 
Version 2.0.3
last update *15-02-2017*

------------------------
>####Table of contents
> - **<a href="#introduction">Introduction</a>**
> - **<a href="#documentation">Documentation</a>**
> - <a href="#getting-started">Getting started</a>
> - <a href="#connection">Connection</a>
> - <a href="#class-functions">Class functions</a>
> - **<a href="#examples">Examples</a>**
> - <a href="#chat-commands">Chat commands</a>

Introduction
-----------------------------

If your server requires a remote connection to a database, stacked up queries can cause noticeable lag in your game server (freezing, players twitching) since MySQL doesn't 'really' queue up the queries. 

I've made a library to fix this problem, it basically queues up the queries and executes them with a dispatched GameThread. It's inspired from the Sourcemod threaded mysql https://wiki.alliedmods.net/SQL_(SourceMod_Scripting)
Remember that all queries now requires a callback, since they are truely dispatched.
 
 This library will automaticly work for Source-python, but if you want to test it in your idle, make sure to grab the corresponding file under /testing/none-python/

Documentation
---------------------
The following section will go into the details of how to implement the threaded MySQL module.

####**Getting started**

- Download the latest <a href="https://github.com/Velocity-plus/threaded_mysql/releases">release</a> 
- Drag the contents of the folder into your /addons/source-python/packages/source-python/..
- Restart your server.


 
 
####**Connection**

The library works as an extension of PyMYSQL, so as any other MySQL script, a connection must be established to a database, but before we can do that, let us initialize the class for threaded MySQL. 
```python
    from threaded_mysql import ThreadedMySQL
    
    TSQL = ThreadedMySQL()
```
After we have initialized our class, we can connect to our MySQL database, you can use Threaded MySQL to connect to your database.
```python
    Available paramenters (host, user, password, db ,charset, cursorclass)
    TSQL.connect(host='localhost', user='root', password='123', db='utf8')
```

If you don't want to connect with Threaded MySQL you can make your connection elsewhere and pass it to Threaded MySQL as soon below with PyMYSQL:
```python
   import pymysql.cursors

   connection = pymysql.connect(host="localhost",
                                    user="root",
                                    password="123",
                                    db="test",
                                    charset="utf8",
                                    cursorclass=pymysql.cursors.DictCursor)

   TSQL.connect_use(connection)
```
Now that our connection has been made, we need to start the thread that handles the queue of queries, as seen below.
```python
    TSQL.handlequeue_start()
```



####**Class functions**
Finally, now we can make use of it. The functions available are listed below
```python
    # Different types of queries availabe
    #    :param query: The SQL query that you want to execute
    #    :param args: If the query have any args
    #    :param callback: The callback for the query
    #    :param data_pack: If you want to pass more to the callback than the query
    #    :param prioritize: If you have large queues prioritizing the query can make it finish
    #     before the rest of the queue is finished
    #    :param get_info: If you want information passed to the callback
    #     (such as timestamp, query and prioritized)
    TSQL.execute(query, args=None, callback=None, data_pack=None, seconds=0.1)
    TSQL.fetchone(query, args=None, callback=None, data_pack=None, seconds=0.1)
    TSQL.fetchall(query, args=None, callback=None, data_pack=None, seconds=0.1)
    
    # Returns the size of the queue
    TSQL.queue_size()

    #If you want to delay the queue for a specific amount time, 1 being 1 seconed
    TSQL.wait(delay)

    # Refreshes the tables
    TSQL.commit()

    # Closes the mysql connection
    TSQL.close()
```

It's important to note that when using the **fetchone** or **fetchall** it will execute the query BEFORE fetching it, so no need to use TSQL.execute when you want to fetch something.

If you want to arguments to the sql query, you can pass them through args=(userid,) - expects a tuple



Examples
--------

If you want to grab the data from **fetchone** or **fetchall** a callback is necessary. To demonstrate this look at the code examples below:

```python
from messages import SayText2
from events import Event
from threaded_mysql import ThreadedMySQL

# Initializes the class
TSQL = ThreadedMySQL()

# Connects to a mysql database
TSQL.connect('localhost', 'root', '123', 'my_database', 'utf8')

# Starts the queuehandler (should only be called once)
TSQL.handlequeue_start()


# The callback from !fetchone
def sql_callback(data):
    name = data['name']
    SayText2(name).send()


# The callback from !fetchall
def sql_callback_2(data, data_pack):
    text = data_pack['text']
    SayText2("You wrote {}".format(text)).send()
    for x in data:
        name = x['name']
        SayText2('Name: {}'.format(name)).send()

# The callback from !info
def sql_callback_3(get_info):
    """
    get_info includes 'query', 'time', 'prioritized'
    """
    query = get_info['query']
    time = get_info['time']
    prio = get_info['prioritized']
    SayText2('Query: {0}\nTime: {1} seconds\nPrioritized: {2}'.format(query, time, prio)).send()



@Event('player_say')
def on_player_say(game_event):
    # What did the player write
    text = game_event['text']

    if text == '!fetchone':
        # Fetches all the names
        TSQL.fetchone('SELECT name FROM my_database', callback=sql_callback)

    if text == '!fetchall':
        # Let's pass some extra things...
        data_pack = {'text': text}
        # Fetches one name
        TSQL.fetchall('SELECT name FROM my_database', callback=sql_callback_2, data_pack=data_pack)

    if text == '!info':
        # Fetches one name
        TSQL.execute("INSERT INTO my_database (name) VALUES('John')", callback=sql_callback_3, get_info=True)
```


####Chat commands

Output !fetchall
> You wrote: !fetchall
> Name: <name >
> Name: <name > 
> (...)

Output !fetchone
> Name: John

Output !info
> Query: INSERT INTO stats (name) VALUES('John')
> Time: 0.014952421188354492 seconds
> Prioritized: False



You can even create tick listener and spam queries without any lag at all

Enjoy :)
