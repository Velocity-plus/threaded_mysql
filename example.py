from messages import SayText2
from events import Event
from threaded_mysql import ThreadedMySQL

# Initializes the class
TSQL = ThreadedMySQL()

# Connects to a mysql database
TSQL.connect('localhost', 'root', '123pass', 'trikz_server', 'utf8')

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
        TSQL.fetchone('SELECT name FROM stats', callback=sql_callback)

    if text == '!fetchall':
        # Let's pass some extra things...
        data_pack = {'text': text}
        # Fetches one name
        TSQL.fetchall('SELECT name FROM stats', callback=sql_callback_2, data_pack=data_pack)

    if text == '!info':
        # Fetches one name
        TSQL.execute('SELECT name FROM stats', callback=sql_callback_3, get_info=True)