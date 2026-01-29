from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from urllib.request import urlopen, urlretrieve
import zipfile
import os
import shutil

CURRENT_VERSION = "1.1"

def Plugins(**kwargs):
    return [PluginDescriptor(name="MarqozzzCUP v%s" % CURRENT_VERSION, 
                            description="Listy kanalow + auto-update", 
                            where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]

def getRemoteVersion():
    try:
        return urlopen("https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/plugin/version.txt").read().decode().strip()
    except:
        return "0.0"

def getDates():
    try:
        dates_raw = urlopen("https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/daty.txt").read().decode()
        dates = {}
        for line in dates_raw.split('\n'):
            if '=' in line:
                name, date = line.split('=', 1)
                dates[name.strip()] = date.strip()
        return dates
    except:
        return {}

def updatePlugin(session):
    try:
        plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/MarqozzzCUP/"
        urlretrieve("https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/MarqozzzCUP-plugin.zip", "/tmp/plugin.zip")
        
        with zipfile.ZipFile("/tmp/plugin.zip", 'r') as z:
            z.extractall(plugin_path)
        
        os.unlink("/tmp/plugin.zip")
        os.chmod(os.path.join(plugin_path, "plugin.py"), 0o755)
        return True
    except:
        return False

def main(session, **kwargs):
    remote_version = getRemoteVersion()
    
    lists = [
        ("Hotbird @Bzyk83 mod. Republika", "https://github.com/marqozzz/MarqozzzCUP-/releases/download/v1-HB-REPUBLIKA/marqozzzcup-complete-HB-REPUBLIKA.zip"),
        ("Hotbird+Astra @Bzyk83 mod. Republika", "https://github.com/marqozzz/MarqozzzCUP-/releases/download/v1-HB-ASTRA-REPUBLIKA/marqozzzcup-complete-HB-ASTRA-REPUBLIKA.zip"),
        ("Hotbird @Bzyk83", "https://github.com/marqozzz/MarqozzzCUP-/releases/download/v1-HB/marqozzzcup-complete-HB.zip"),
        ("Hotbird+Astra @Bzyk83", "https://github.com/marqozzz/MarqozzzCUP-/releases/download/v1-HB-ASTRA/marqozzzcup-complete-HB-ASTRA.zip")
    ]
    
    dates = getDates()
    lists_display = []
    
    if remote_version > CURRENT_VERSION:
        lists_display.append(("Nowa wersja %s dostepna. Aktualizowac z %s?" % (remote_version, CURRENT_VERSION), "UPDATE", None))
    else:
        lists_display.append(("Plugin aktualny v%s" % CURRENT_VERSION, "CURRENT", None))
    
    for name, url in lists:
        date = dates.get(name, "brak daty")
        display = "%s (%s)" % (name, date)
        lists_display.append((display, url))
    
    session.openWithCallback(lambda choice: choiceCallback(session, choice), 
                            ChoiceBox, title="MarqozzzCUP v%s" % CURRENT_VERSION, list=lists_display)

def choiceCallback(session, choice):
    if choice and choice[1]:
        if choice[1] == "UPDATE":
            session.openWithCallback(lambda confirmed: updateConfirm(session, confirmed), 
                                   MessageBox, text="Zaktualizowac plugin do v%s?" % getRemoteVersion(), 
                                   type=MessageBox.TYPE_YESNO)
        elif choice[1] == "CURRENT":
            session.open(MessageBox, text="Masz najnowsza wersja pluginu v%s!" % CURRENT_VERSION, type=MessageBox.TYPE_INFO, timeout=2)
        else:
            url = choice[1]
            full_name = choice[0]
            session.openWithCallback(lambda confirmed: confirmCallback(session, confirmed, url, full_name), 
                                   MessageBox, text="Zainstalowac liste?\n\n%s" % full_name, 
                                   type=MessageBox.TYPE_YESNO)

def updateConfirm(session, confirmed):
    if confirmed:
        if updatePlugin(session):
            session.open(MessageBox, text="Plugin zaktualizowany!\nDekoder zostanie zrestartowany za 5 sekund...", 
                        type=MessageBox.TYPE_INFO, timeout=5)
            os.system("(sleep 5 && killall -9 enigma2) &")
        else:
            session.open(MessageBox, text="Blad aktualizacji pluginu!", type=MessageBox.TYPE_ERROR)

def confirmCallback(session, confirmed, url, full_name):
    if confirmed:
        installList(session, url, full_name)

def installList(session, url, full_name):
    try:
        print("MarqozzzCUP: %s" % full_name)
        
        if os.path.exists("/etc/enigma2/bouquets.tv"):
            shutil.copy2("/etc/enigma2/bouquets.tv", "/etc/enigma2/bouquets.tv.bak")
        
        urlretrieve(url, "/tmp/list.zip")
        os.makedirs("/tmp/list_unpack", exist_ok=True)
        
        with zipfile.ZipFile("/tmp/list.zip", 'r') as z:
            z.extractall("/tmp/list_unpack/")
        
        files_copied = 0
        for root, dirs, files in os.walk("/tmp/list_unpack"):
            for file in files:
                src = os.path.join(root, file)
                dst = "/etc/enigma2/" + file
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                    files_copied += 1
        
        os.unlink("/tmp/list.zip")
        shutil.rmtree("/tmp/list_unpack")
        
        session.open(MessageBox, text="Lista zainstalowana!\n%s\nPlikow: %d\nDekoder zostanie zrestartowany za 5 sekund..." % (full_name, files_copied), 
                     type=MessageBox.TYPE_INFO, timeout=5)
        
        os.system("(sleep 5 && killall -9 enigma2) &")
        
    except Exception as e:
        session.open(MessageBox, text="Blad instalacji!\n%s\n%s" % (full_name, str(e)), type=MessageBox.TYPE_ERROR)
