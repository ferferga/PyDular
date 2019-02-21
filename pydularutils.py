import logging
import sqlite3
from telethon import TelegramClient, sync, events
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import *
from telethon.tl.custom import *
from telethon.tl.types import *
from telethon.utils import *
from telethon.sessions import *
import json
import db_handler
import sys

__log__ = logging.getLogger(__name__)
recreate = True ##Sets whether the database needs to be recreated again.
answer_strangers = True
UserIDs = []
UserNames = []
UserClass = []

class PyDularLoadFail(Exception):
    pass

class PyDularFail(Exception):
    pass

def LoadException():
    __log__.error("PyDular could not load, with a catched exception. Check log. Log closed!")
    sys.exit(1)

def RuntimeException():
    __log__.error("PyDular experienced a runtime error, with a catched exception. Check log. Log closed!")
    sys.exit(1)

def LoadUnknownException(e):
    __log__.exception("PyDular is no longer running due to an unknown exception. Stacktrace: \n\n" + str(e))
    __log__.info("Report this incident, please. Log closed!")
    sys.exit(1)

def LoadExcept(e):
    __log__.exception("Unknown exception. Full stacktrace:\n\n" + str(e))
    raise PyDularLoadFail

def RunExcept(e):
    __log__.exception("Unknown exception. Full stacktrace:\n\n" + str(e))
    raise PyDularFail

def load():
    global __log__, config, strings, bot, recreate
    try:
        with open('data/config.json', 'r', encoding="utf-8") as f:
            config = json.load(f)
        try:
            with open("data/languagues/" + config['lang'] + ".json", 'r', encoding="utf-8") as f:
                strings = json.load(f)
        except FileNotFoundError:
            __log__.error("There is no appropiate lang .json file in the data/languagues folder. Exiting PyDular...")
            raise PyDularLoadFail
        except Exception as e:
            LoadExcept(e)
        if str(config['recreate']).lower() == "true":
            recreate = True
        elif str(config['recreate']).lower() == "false":
            recreate = False
        else:
            __log__.error("'Recreate' parameter is set incorrectly. Exiting PyDular")
            raise PyDularLoadFail
        __log__.info(".JSON files loaded correctly")
    except FileNotFoundError:
        __log__.error("Config file file doesn't exists. Make sure that the configuration file exists")
        raise PyDularLoadFail
    except Exception as e:
        LoadExcept(e)
    try:
        bot = TelegramClient("data/tg-session-data", int(config['api-id']), config['api-hash'])
        __log__.info("TelegramClient instantiated succesfully! Parameters in config.json seems good at this point.")
    except Exception as e:
        __log__.error("There was a problem when instantiating the client, \
        ApiID or ApiHash is incorrect or telethon is missing in your system o virtualenv")
    db_handler.init()

def CreateKeyboard(diction):
    Butt = []
    RowButt = []
    for loop, name in enumerate(diction):
        if loop%4 == 0 and loop != 0:
            Butt.append(tuple(RowButt))
            RowButt.clear()
            but = Button.text(name, resize=True, single_use=True)
            RowButt.append(but)
        else:
            but = Button.text(name, resize=True, single_use=True)
            if len(name)>35:
                Butt.append(but)
            else:
                RowButt.append(but)
    if len(RowButt) != 0:
        Butt.append(tuple(RowButt))
        RowButt.clear()
    return Butt