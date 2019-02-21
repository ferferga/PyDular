import logging
import os
import pydularutils
import db_handler
import sys
import importlib
from telethon import TelegramClient, sync, events
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import *
from telethon.tl.custom import *
from telethon.tl.types import *
from telethon.utils import *
from telethon.sessions import *
import importlib

modules = []
modnames = []

if __name__ == "__main__":
    if os.path.isfile("PyDular-log.log"):
        os.remove("PyDular-log.log")
logging.basicConfig(handlers=[logging.FileHandler("PyDular-log.log", 'w', 'utf-8')], level=logging.NOTSET, format="%(asctime)s %(levelname)s: %(message)s")
logging.getLogger(__name__).addHandler(logging.NullHandler())
__log__ = logging.getLogger(__name__)
logging.info('Starting PyDular...')

try:
    pydularutils.load()
except pydularutils.PyDularLoadFail:
    pydularutils.LoadException()
except Exception as e:
    pydularutils.LoadUnknownException(e)

from pydularutils import bot, config, strings, answer_strangers
from db_handler import exists

try:
    bot.start(bot_token=config['bot-token'])
    if bot.is_user_authorized():
        __log__.info("Bot logged in succesfully!")
        if db_handler.exists is False:
            db_handler.com_query("UPDATE users SET class = 1 WHERE id = " + str(bot.get_me().id))
    else:
        __log__.info(
            "Bot couldn't be logged in. Connection errors should be handled by Telethon wrapper, \
            \nso this is more likely a problem in your bot token.")
        raise pydularutils.PyDularLoadFail
except pydularutils.PyDularLoadFail:
    pydularutils.LoadException()
except Exception as e:
    pydularutils.LoadUnknownException(e)

## METHODS
## Get modules in subfolders
def GetModules():
    global modules
    lst = os.listdir("modules")
    for d in lst:
        s = os.path.abspath("modules") + os.sep + d
        if os.path.isdir(s) and os.path.exists(s + os.sep + "__init__.py"):
            modules.append(d)
    for name in modules:
        name = "modules." + name
        mod = importlib.import_module(name)
        try:
            __log__.info("Module " + str(mod.name) + " with version " + str(mod.version) + " is loaded!")
        except:
            __log__.info("Module under subfolder " + name + " isn't recognised. Check documentation!")
            modules.remove(name)

## Executes the specified module
def LoadModule(name):
    mod = importlib.import_module("modules." + name)
    return mod

## Main event chain
@bot.on(events.NewMessage)
async def my_event_handler(event):
    if '/start' in event.raw_text and config['rootUser'] == "":
        await event.reply(strings['welcome-first'] + str(get_peer_id(await event.get_sender())) + '**')
    elif ('/start' in event.raw_text and not (config['rootUser'] == "")) or not (config['rootUser'] == ""):
        user = await bot.get_entity(int(config['rootUser']))
        if get_peer_id(await event.get_sender()) == int(config['rootUser']):
            if strings['start-modules'] == event.raw_text:
                markup = pydularutils.CreateKeyboard(modnames)
                await event.reply(strings["your-modules"], buttons=markup)
                markup.clear()
            elif strings['settings-button'] == event.raw_text:
                markup = pydularutils.CreateKeyboard([strings["user-settings"], strings["module-settings"],
                strings["pydular-settings"], strings["about"]])
                await event.reply(strings["settings-description"], buttons=markup)
            elif event.raw_text in modnames:
                mod = LoadModule(modules[modnames.index(event.raw_text)])
                mod.main()
            else:
                await event.reply(strings['settings-welcome1'] + user.first_name + strings['settings-welcome2root'], 
                buttons=[Button.text(strings['settings-button'], resize=True, single_use=True), Button.text(strings['start-modules'], resize=True, single_use=True)])
        else:
            __log__.warning("Non-root user talking!")
    else:
        pass

try:
    __log__.info("PyDular Load completed! Listening for events...")
    GetModules()
    ## Gathers modules names (in case you want to change the sub-folder name, it still keeps being the sdisplayed the same way)
    for m in modules:
        mod = LoadModule(m)
        modnames.append(mod.name)
    bot.run_until_disconnected()
except pydularutils.PyDularFail:
    pydularutils.RuntimeException()
except Exception as e:
    pydularutils.RunExcept(e)
except KeyboardInterrupt:
    __log__.info("Keyboard Interruption. Closing PyDular...")
    db_handler.db_conn().close()
    sys.exit(0)

