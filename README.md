**Threaded MySQL**
-------------
Tired of lag?

If your server requires a remote connection to a database, stacked up queries can cause noticeable lag in your game server (freezing, players twitching) since MySQL doesn't 'really' queue up the queries. 

I've made a library to fix this problem, it basically queues up the queries and executes them after a certain delay (that can be modified).
 It's inspired from the Sourcemod threaded MySQL https://wiki.alliedmods.net/SQL_(SourceMod_Scripting) Remember that all queries now requires a callback, since they are dispatched.
 
 This library will only work for Source-python, but I am working on a version for regular use.
 

**Documentation**
-------------

The library works as an extension of PyMYSQL, so as any other MySQL script, a connection must be established to a database, but before we can do that, let us initialize the class for threaded MySQL. 
```python
    from threaded_mysql import ThreadedMySQL
    
    TSQL = ThreadedMySQL()
```
After we have initialized our class, we can connect to our MySQL database (in future updates, you can create the connection elsewhere and pass it into the class, but for now..).
```python
    Available paramenters (host, user, password, db ,charset, cursorclass)
    TSQL.connect(host='localhost', user='root', password='123', db='utf8')
```
Now that our connection has been made, we need to start the thread that handles the queue of queries, as seen below.
```python
    TSQL.handlequeue_start()
```
Finally, now we can make use of it. The functions available are listed below
```python
    # Different types of queries availabe
    TSQL.execute(query, args=None, callback=None, data_pack=None, seconds=0.1)
    TSQL.fetchone(query, args=None, callback=None, data_pack=None, seconds=0.1)
    TSQL.fetchall(query, args=None, callback=None, data_pack=None, seconds=0.1)
    
    # Refresh the tables
    TSQL.commit()

    # Closes the connection to the database
    TSQL.close()
```

It's important to note that when using the **fetchone** or **fetchall** it will execute the query BEFORE fetching it, so no need to use TSQL.execute when you want to fetch something.

If you want to grab the data from **fetchone** or **strong text**fetchall a callback is necessary. To demonstrate this look at the code examples below:

**Code examples**
-------------
```python
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
                 TSQL.fetchone('SELECT name FROM database_example', callback=sql_callback_2, data_pack=data_pack)
```
> Output !fetchall
> =>  [{'name': John'}, {'name': 'Daniel'}.... 
> 
> Output !fectone
> =>  ['name': John']
> => You wrote !fetchone



You can even create tick listener and spam queries without any lag at all

Enjoy :)
