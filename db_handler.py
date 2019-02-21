import sqlite3
import os
import logging
import version
import pydularutils
__log__ = logging.getLogger(__name__)

exists = True
needs_updating = False
version = version.__version__
db_version = 1

EntID = []
EntName = []
EntUsername = []
EntClass = []

##Helper methods
def db_error(e):
    if pydularutils.recreate:
        __log__.error("DATABASE INTEGRITY ERROR! Full stacktrace:\n\n" + str(e) + "\n\nRecreating database per-settings.")
    else:
        __log__.error("DATABASE INTEGRITY ERROR! Full stacktrace:\n\n" + str(e))

def db_conn():
    conn = sqlite3.connect("data/PyDular-data.db")
    return conn

def com_query(*args, **kwargs):
    c = db_conn()
    c.execute(*args, **kwargs)
    c.commit()

##Creates the database
def InitDB(db):
    d = db.cursor()
    d.execute("CREATE TABLE pydular_info (version REAL, db_version REAL)")
    d.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, name TEXT, class INTEGER)")
    d.execute("CREATE TABLE modules (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
    d.execute("CREATE TABLE settings (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, value INTEGER)")
    d.execute("CREATE TABLE permissions (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
    db.commit()
    reg = (float(version), float(db_version))
    db.execute("INSERT INTO pydular_info VALUES(?,?)", reg)
    reg1 = (None, "answer_strangers", 0)
    db.execute("INSERT INTO settings VALUES(?,?,?)", reg1)
    db.commit()
    __log__.info("Database created successfully!")

## Load settings for later use
def LoadDB():
    global EntID, EntUsername, EntName
    checkList = []
    l = 0
    conn = sqlite3.connect("data/tg-session-data.session").cursor()
    c = db_conn()
    cur = c.cursor()
    conn.execute("SELECT * FROM entities")
    for row in conn:
        EntID.append(row[0])
        EntUsername.append(row[2])
        EntName.append(row[4])
    cur.execute("SELECT * FROM users")
    for r in cur:
        checkList.append(r[0])
    for i in EntID:
        if i not in checkList:
            rege = (i, EntUsername[EntID.index(i)], EntName[EntID.index(i)], None)
            c.execute("INSERT INTO users VALUES(?,?,?,?)", rege)
        else:
            continue
    c.commit()
    checkList.clear()
    if pydularutils.config['rootUser'] != "":
        cur.execute("SELECT * FROM users WHERE id = " + pydularutils.config['rootUser'])
        for r in cur:
            l = l + 1
        if l == 0:
            __log__.error("""The root user hasn't been seen by the bot yet. You must talk with the bot first in order to set it up. 
            Run the bot, start a conversation with the bot using the user you want to be root, note your id and set it on config.json. Read the manual for more info""")
            raise pydularutils.PyDularLoadFail
        else:
            com_query("UPDATE users SET class = 2 WHERE class = 4 AND id != " + pydularutils.config['rootUser'])
            com_query("UPDATE users SET class = 4 WHERE id = " + pydularutils.config['rootUser'])

##We will only take care here if the file exists. If the database is corrupted, exceptions will be handled afterwards.
def CheckDB():
    global exists
    if os.path.isfile("data/PyDular-data.db"):
        exists = True
    else:
        exists = False
    return exists

def UpdDB(db):
    global needs_updating
    q = db.cursor()
    q.execute("SELECT * FROM pydular_info")
    for row in q:
        if row[0] == float(version):
            __log__.info("Database is updated")
        else:
            __log__.info("Database needs updating!")
            needs_updating = True
            db.execute("UPDATE pydular_info SET version = '" + version + "'")

##Initialization
def init():
    if CheckDB():
        __log__.info("Database exists. Loading data into RAM...")
        LoadDB()
        __log__.info("Checking if database needs updating...")
        UpdDB(db_conn())
    else:
        __log__.info("Database doesn't exist. Creating database...")
        InitDB(db_conn())
        LoadDB()