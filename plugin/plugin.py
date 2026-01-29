from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from urllib.request import urlopen, urlretrieve
import zipfile
import os
import shutil

def Plugins(**kwargs):
    return [PluginDescriptor(name="MarqozzzCUP", 
                            description="4 listy kanałów do wyboru", 
                            where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]

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

def main(session, **kwargs):
    lists = [
        ("Hotbird @Bzyk83 mod. Republika", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB-REPUBLIKA.zip"),
        ("Hotbird+Astra @Bzyk83 mod. Republika", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB-ASTRA-REPUBLIKA.zip"),
        ("Hotbird @Bzyk83", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB.zip"),
        ("Hotbird+Astra @Bzyk83", "https://raw.githubusercontent.com/marqozzz/MarqozzzCUP-/main/lists/marqozzzcup-complete-HB-ASTRA.zip")
    ]
    
    dates = getDates()
    lists_with_date = []
    for name, url in lists:
        date = dates.get(name, "brak daty")
        lists_with_date.append(("%s (%s)" % (name, date), url))
    
    session.openWithCallback(lambda choice: choiceCallback(session, choice), 
                            ChoiceBox, title="Wybierz listę:", list=lists_with_date)

# reszta bez zmian...
def choiceCallback(session, choice):
    if choice and choice[1]:
        url = choice[1]
        full_name = choice[0]
        session.openWithCallback(lambda confirmed: confirmCallback(session, confirmed, url, full_name), 
                                MessageBox, text="Zainstalować:\n%s?" % full_name, type=MessageBox.TYPE_YESNO)

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
        
        session.open(MessageBox, text="✅ %s\nPlików: %d\nRestart za 5s" % (full_name, files_copied), 
                     type=MessageBox.TYPE_INFO, timeout=5)
        os.system("(sleep 5 && killall -9 enigma2) &")
        
    except Exception as e:
        session.open(MessageBox, text="❌ BŁĄD %s:\n%s" % (full_name, str(e)), type=MessageBox.TYPE_ERROR)
